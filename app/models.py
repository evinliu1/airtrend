from typing import List, Optional
from pydantic import BaseModel

class Location(BaseModel):
    id: int
    name: str
    locality: Optional[str]
    country_code: str
    provider_name: Optional[str]
    latitude: float
    longitude: float

class LocationPage(BaseModel):
    data: List[Location]
    page: int
    per_page: int
    total: int
    total_pages: int

class Trend(BaseModel):
    location_id: int
    name: str
    locality: Optional[str]
    country_code: str
    latitude: float
    longitude: float
    parameter_name: str
    slope: float
    r2: Optional[float]
    mean_value: Optional[float]
    years_used: int
    first_year: int
    last_year: int

class TrendPage(BaseModel):
    data: List[Trend]
    page: int
    per_page: int
    total: int
    total_pages: int