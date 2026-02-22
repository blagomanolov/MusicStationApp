import pycountry
from sqlalchemy import select
import logging
from sqlalchemy.ext.asyncio import AsyncResult
from typing import List, Optional



from database.database import Database
from lib.models import Country


class PopulateCountryHandler:
    def __init__(self, db_template: Database):
        self.db_template: Database = db_template
        self.logger: logging.Logger = logging.getLogger(__name__)
    
    async def populate_countries(self) -> None:
        self.logger.info("Starting contry population ...")
        await self.db_template.create_all()

        async with self.db_template.session() as db:
            result: AsyncResult = await db.execute(select(Country))
            countries: List[Country] = result.scalars().all()

            if countries:
                self.logger.info("Country table already populated. Skipping population.")
            
            for country in pycountry.countries:
                code: str = country.alpha_2
                name: str = country.name

                result: AsyncResult = await db.execute(select(Country).where(Country.code==code))
                existing: Optional[Country] = result.scalar_one_or_none()
                if existing:
                    continue

                new_country: Country = Country(code=code, name=name)
                db.add(new_country)
                self.logger.info(f"Added: {name} - ({code})")

        self.logger.info("Country population completed.")
    