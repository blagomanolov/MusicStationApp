import logging
import logging.config
from typing import Optional, Tuple, List
import os
import io

import requests
from fastapi import FastAPI, Request, Query, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, func, Select
from sqlalchemy.ext.asyncio import AsyncSession, AsyncResult

from database.database import Database
from lib.models import Station, Country, Song
from lib.schemas import StationCreate, StationRead
from lib.crud import create_station, create_song
from lib.populate_country import PopulateCountryHandler
from lib.populate_station import StationHandler
from configs.config import Config
from configs.logging_config import LOGGING_CONFIG

app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), 'templates'))

db_instance: Optional[Database] = None  

async def get_db() -> AsyncSession:
    async with db_instance.session() as session:
        yield session

@app.on_event("startup")
async def startup_event():
    global db_instance
    configs: Config = Config()
    logging.config.dictConfig(LOGGING_CONFIG)
    logger: logging.Logger = logging.getLogger(__name__)

    db_instance = Database(configs.database_path)
    await db_instance.create_all()

    country_handler: PopulateCountryHandler = PopulateCountryHandler(db_instance)
    await country_handler.populate_countries()

    station_handler: StationHandler = StationHandler(
        api_url=configs.station_api_url,
        db_template=db_instance
    )
    await station_handler.run()


@app.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    genre: Optional[str] = None,
    country: Optional[str] = None,
    q: Optional[str] = None,
):
    per_page: int = 10
    stmt: Select[Station] = select(Station)
    if q:
        stmt = stmt.filter(Station.name.ilike(f"%{q}%"))
    if genre:
        stmt = stmt.filter(Station.genre.ilike(f"%{genre}%"))
    if country:
        stmt = stmt.filter(Station.country_code == country)
    
    count_stmt: Select[Tuple[int]] = select(func.count()).select_from(stmt.subquery())
    count_result: AsyncResult = await db.execute(count_stmt)
    total_count: int = count_result.scalar_one()

    result: AsyncResult = await db.execute(stmt.offset((page - 1) * per_page).limit(per_page))
    stations: List[Station] = result.scalars().all()

    genres_result: AsyncResult = await db.execute(select(Station.genre).distinct())
    genres: List[str] = [g[0] for g in genres_result.all() if g[0]]

    countries_result: AsyncResult = await db.execute(select(Country).order_by(Country.name))
    countries: List[Country] = countries_result.scalars().all()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "stations": stations,
            "genres": genres,
            "countries": countries,
            "selected_genre": genre,
            "selected_country": country,
            "selected_query": q,
            "page": page,
            "total_pages": (total_count + per_page - 1) // per_page,
        },
    )


@app.post("/station/create", response_model=StationRead)
async def create_station_endpoint(station: StationCreate, db: AsyncSession = Depends(get_db)):
    result: AsyncResult = await db.execute(select(Station).where(Station.name == station.name))
    existing: Optional[Station] = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=404, detail="Station with this name already exists.")

    new_station: Station = await create_station(db, station)  
    return new_station


@app.post("/stations/{slug}/favorite")
async def toggle_favorite(slug: str, request: Request, db: AsyncSession = Depends(get_db)):
    result: AsyncResult = await db.execute(select(Station).where(Station.slug == slug))
    station: Optional[Station] = result.scalar_one_or_none()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found!")

    station.is_favorite = not station.is_favorite
    db.add(station)
    await db.commit()

    referer: str = request.headers.get("referer") or "/"
    return RedirectResponse(url=referer, status_code=status.HTTP_303_SEE_OTHER)


@app.get("/favorites", response_class=HTMLResponse)
async def favorites(request: Request, db: AsyncSession = Depends(get_db)):
    result: AsyncResult = await db.execute(select(Station).where(Station.is_favorite.is_(True)).order_by(Station.name.asc()))
    stations: List[Station] = result.scalars().all()

    countries_result: AsyncResult = await db.execute(select(Country).order_by(Country.name))
    countries: List[Country] = countries_result.scalars().all()

    return templates.TemplateResponse(
        "favorites.html",
        {"request": request, "stations": stations, "countries": countries},
    )


@app.get("/songs", response_class=HTMLResponse)
async def songs(request: Request, db: AsyncSession = Depends(get_db)):
    result: AsyncResult = await db.execute(select(Song).order_by(Song.name))
    songs: List[Song] = result.scalars().all()
    return templates.TemplateResponse("songs.html", {"request": request, "songs": songs})


@app.post("/songs/{song_id}/delete")
async def delete_song(song_id: int, db: AsyncSession = Depends(get_db)):
    result: AsyncResult = await db.execute(select(Song).where(Song.id == song_id))
    song: Optional[Song] = result.scalar_one_or_none()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    await db.delete(song)
    await db.commit()
    return RedirectResponse(url="/songs", status_code=303)


@app.get("/stations/{slug}/play", response_class=HTMLResponse)
async def play_station(slug: str, request: Request, db: AsyncSession = Depends(get_db)):
    result: AsyncResult = await db.execute(select(Station).where(Station.slug == slug))
    station: Optional[Station] = result.scalar_one_or_none()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found!")

    country_name: str = station.country.name if station.country else "Unknown"
    return templates.TemplateResponse(
        "station.html", {"request": request, "station": station, "country_name": country_name}
    )


@app.get("/stations/{slug}/recognize")
async def recognize_song(slug: str, db: AsyncSession = Depends(get_db)):
    result: AsyncResult = await db.execute(select(Station).where(Station.slug == slug))
    station: Optional[Station] = result.scalar_one_or_none()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    stream_url: str = station.url
    headers: dict = {"Icy-MetaData": "1"}

    try:
        r: requests.Response = requests.get(stream_url, headers=headers, stream=True, timeout=10)
        meta_int: int = int(r.headers.get("icy-metaint", 0))
        if not meta_int:
            return {"song": "No ICY metadata in this stream"}

        stream: io.BufferedReader = r.raw
        stream.read(meta_int)
        metadata_length: int = ord(stream.read(1)) * 16
        metadata: bytes = stream.read(metadata_length).rstrip(b"\0")

        text: str = metadata.decode(errors="ignore")
        if "StreamTitle=" in text:
            title: Optional[str] = text.split("StreamTitle='")[1].split("';")[0]
            return {"song": title or "Unknown song"}
        return {"song": "No title found"}

    except Exception as e:
        return {"song": f"Error: {str(e)}"}


@app.post("/songs/add")
async def add_song(name: str = Query(...), db: AsyncSession = Depends(get_db)):
    song: Song = await create_song(db, name)
    return {"message": f"Song '{song.name}' added to database"}
