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