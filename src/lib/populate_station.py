import logging
import json
import requests
from requests.models import Response
import re
from typing import Optional, List, Set
import slugify
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncResult


from database.database import Database
from configs.constants import GENRE_SYNONYMS, BRACKETS_RE, SEPARATORS_RE, GENERIC_WORDS, SPACES_RE
from lib.schemas import StationCreate
from lib.models import Station
from sqlalchemy.exc import IntegrityError

class StationHandler:
    KEYWORD_INDEX: List[tuple] = []
    CANONICAL_KEYWORDS: List[str] = list(GENRE_SYNONYMS.keys())

    def __init__(self, api_url: str, db_template: Database):
        self.api_url: str = api_url
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.db_template: Database = db_template

        self._fill_genre_synonyms()

    async def run(self):
        try:
            stations: Optional[List] = self._get_stations()
            await self._get_necessary_data(stations)
        except Exception as e:
            raise e

    def _get_stations(self) -> Optional[List]:
        response: Response = requests.get(self.api_url)
        stations: List = response.json()
        if stations:
            return stations
    
    from sqlalchemy.exc import IntegrityError

    async def _get_necessary_data(self, stations: list):
        for station in stations:
            genre_text_parts: List[str] = []
            orginal_station_name: str = station.get("name", "")
            normalized_name: str = self._normalized_station_name(orginal_station_name)

            if not normalized_name or not normalized_name.strip():
                self.logger.info(f"Skipping station with invalid name: {orginal_station_name}")
                continue

            stream_url: str = station.get("url_resolved", "")
            if not stream_url:
                self.logger.info(f"Skipping station without stream URL: {normalized_name}")
                continue

            slug: str = slugify.slugify(normalized_name)
            country_code: str = self._generate_country_code(station.get("countrycode", ""))

            genre_text_parts.extend([
                orginal_station_name or "",
                stream_url or "",
                station.get("homepage", "") or "",
                station.get("country", "") or "",
                station.get("language", "") or "",
                station.get("tags", "") or ""
            ])
            genre_corpus: str = " | ".join([part for part in genre_text_parts if part])
            genre: str = self._infer_genres_from_text(genre_corpus)

            try:
                static_data: StationCreate = StationCreate(
                    name=normalized_name,
                    url=stream_url,
                    genre=genre,
                    country_code=country_code
                )
            except Exception as e:
                self.logger.warning(
                    f"Skipping station due to validation error: {orginal_station_name} | Error: {e}"
                )
                continue  

            data: dict = static_data.model_dump()
            data['url'] = str(data['url'])
            new_station: Station = Station(**data, slug=slug)

            async with self.db_template.session() as session:
                existing_station: AsyncResult = await session.execute(select(Station).where(Station.slug == slug))
                existing_station: Optional[Station] = existing_station.scalar_one_or_none()

                if existing_station:
                    self.logger.info(f"Skipping station with duplicate slug: {slug} | {normalized_name}")
                    continue  

                try:
                    session.add(new_station)
                    await session.commit()  
                    self.logger.info(f"Added station: {normalized_name}")
                except IntegrityError as e:
                    self.logger.warning(f"IntegrityError while adding station: {normalized_name} | Error: {e}")
                    await session.rollback() 
                    continue
                except Exception as e:
                    self.logger.error(f"Unexpected error while adding station: {normalized_name} | Error: {e}")
                    await session.rollback()  
                    continue

    
    def _infer_genres_from_text(self, genre_text: str) -> str:
        if not genre_text:
            return "Unknown"
        haystack: str = genre_text.lower()
        matched: Set[str] = set()

        for canonical, variant in self.KEYWORD_INDEX:
            if variant in haystack:
                matched.add(canonical)
        
        if not matched:
            return "Unknown"
        
        ordered: List[str] = [g for g in self.CANONICAL_KEYWORDS if g in matched]
        return ", ".join(ordered)


    def _fill_genre_synonyms(self):
        for canonical, variants in GENRE_SYNONYMS.items():
            for variant in variants:
                self.KEYWORD_INDEX.append((canonical, variant.lower()))

    def _generate_country_code(self, country_code: str) -> str:
        if country_code:
            if len(country_code.strip()) == 2:
                return country_code
            return "UN"

    def _normalized_station_name(self, station_name: str) -> str:
        if not station_name:
            return "Unknown Station"
        station_name = BRACKETS_RE.sub("", station_name).strip()
        
        candidate: str = station_name
        parts: List = [
            part.strip()
            for part in SEPARATORS_RE.split(station_name)
            if part.strip()
        ]

        if parts:
            candidate: str = parts[0]
            return self._remove_generic_suffixes_prefixes(candidate)
            
        candidate: str = self._remove_generic_suffixes_prefixes(station_name)
        return candidate or station_name
        

    def _remove_generic_suffixes_prefixes(self, station_name: str) -> str:
        words: List = [
            word for word in re.split(r"\s+", station_name)
            if word
        ]
        words: List = [
            word for word in words if word.lower() not in GENERIC_WORDS
        ]

        if not words:
            words: str = [station_name]
        cleaned: str = SPACES_RE.sub(" ", " ".join(words).strip())
        return cleaned if cleaned else None

