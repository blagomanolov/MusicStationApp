from typing import Optional, Annotated
from pydantic import (
    BaseModel, ConfigDict, StringConstraints, HttpUrl
)

CountryCode: Annotated = Annotated[
    str, StringConstraints(min_length=2, max_length=2, pattern=r"^[A-Z]{2}$")
]

NameStr: Annotated = Annotated[
    str, StringConstraints(min_length=1, max_length=255)
]

GenreStr: Annotated = Annotated[
    str, StringConstraints(min_length=1, max_length=100)
]

class CountryCreate(BaseModel):
    code: CountryCode
    name: NameStr

class CountryRead(BaseModel):
    code: CountryCode
    name: NameStr

    model_config = ConfigDict(from_attributes=True)

class StationCreate(BaseModel):
    name: NameStr
    genre: Optional[GenreStr] = None
    url: HttpUrl
    country_code: CountryCode
    is_favorite: bool = False

class StationRead(BaseModel):
    id: int
    name: NameStr
    genre: Optional[GenreStr] = None
    url: HttpUrl
    slug: Optional[str] = NameStr
    country_code: CountryCode
    is_favorite: bool

    model_config = ConfigDict(from_attributes=True)

class SongCreate(BaseModel):
    name: NameStr

class SongRead(BaseModel):
    id: int
    name: NameStr
