from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession, AsyncResult
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from lib.models import Station, Song
from lib.schemas import StationCreate

async def create_station(
        db: AsyncSession, station: StationCreate, slug: str) -> Optional[Station]:

    result: AsyncResult = await db.execute(select(Station).filter(Station.slug==slug))
    existing_station: Optional[Station] = result.scalars().first()
    if existing_station:
        return existing_station

    db_station: Station = Station(
        name=station.name,
        genre=station.genre,
        url=station.url,
        country_code=station.country_code,
        is_favorite=getattr(station, 'is_favorite', False),
        slug=slug
    )

    try:
        db.add(db_station)
        await db.commit()
        await db.refresh(db_station)
    except IntegrityError:
        await db.rollback()
        return None
    return db_station

async def get_station(db: AsyncSession, station_slug: str) -> Optional[Station]:
    result: AsyncResult = await db.execute(select(Station).filter(Station.slug==station_slug))
    return result.scalars().first()

async def create_song(db: AsyncSession, name: str) -> Optional[Song]:
    result: AsyncResult = await db.execute(select(Song).filter(Song.name==name))
    existing_song: Optional[Song] = result.scalars().first()
    if existing_song:
        return existing_song
    
    song: Song = Song(name=name)
    db.add(song)
    try:
        await db.commit()
        await db.refresh(song)
    except IntegrityError:
        await db.rollback()
        return None
    return song

