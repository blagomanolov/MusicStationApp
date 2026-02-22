from sqlalchemy import Integer, String, ForeignKey, event, Boolean, text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from slugify import slugify
from typing import List, Optional

from database.database import Base

class Country(Base):
    __tablename__ = 'countries'

    code: Mapped[str] = mapped_column(String(2), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    
    stations: Mapped[List["Station"]] = relationship(
        back_populates="country",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

class Station(Base):
    __tablename__ = 'stations'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    genre: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    url: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True)
    country_code: Mapped[str] = mapped_column(String(2), ForeignKey("countries.code", ondelete="CASCADE"), index=True)
    is_favorite: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))

    country: Mapped["Country"] = relationship(
        back_populates="stations",
        lazy="selectin"
    )

class Song(Base):
    __tablename__ = "songs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

@event.listens_for(Station, "before_insert")
def generate_slug(mapper, connection, target: Station):
    if not target.slug and target.name:
        target.slug = slugify(target.name)