from typing import AsyncGenerator
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine
)
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Database:
    def __init__(self, database_path: Path): 
        self._database_path: Path = database_path
        self._database_url: str = self._create_database_url()
        self.logger: logging.Logger = logging.getLogger(__name__)
    
        self.logger.info("Enitializing database connection ...")
        self._engine: AsyncEngine = self._create_engine()
        self._sessionmaker: async_sessionmaker = async_sessionmaker(
            bind=self._engine, expire_on_commit=False, autoflush=False
        )
        self.logger.info("Database initialized successfully.")
    
    def _create_engine(self) -> AsyncEngine:
        try:
            engine: AsyncEngine = create_async_engine(
                self._database_url,
                echo=False,
                pool_pre_ping=True,
                connect_args={"check_same_thread": False}
            )
            self.logger.info("Async engine created.")
            return engine
        except Exception as e:
            self.logger.exception("Failed to create database engine")
            raise

    def _create_database_url(self) -> str:
        return f"sqlite+aiosqlite:///{self._database_path}"

    @property
    def engine(self) -> AsyncEngine:
        return self._engine
    
    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        self.logger.info("Opening database session.")
        async with self._sessionmaker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                self.logger.exception("Database session error. Rolling back")
                await session.rollback()
                raise
            finally:
                self.logger.info("Closing database session.")
        
    async def create_all(self) -> None:
        self.logger.info("Creating database tables ...")
        try:
            async with self._engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            self.logger.info("Tables created successfully.")
        except Exception as e:
            self.logger.exception("Error while creating tables.")
            raise
    
    async def dispose(self) -> None:
        self.logger.info("Disposing database engine ...")
        try:
            await self._engine.dispose()
            self.logger.info("Database engine disposed.")
        except Exception:
            self.logger.exception("Error while disposing engine.")
            raise
