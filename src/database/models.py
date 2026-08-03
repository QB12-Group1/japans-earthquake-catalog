from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class EarthquakeCategory(StrEnum):
    WEAK = "Weak"
    MODERATE = "Moderate"
    STRONG = "Strong"


class EarthquakeSource(StrEnum):
    USGS = "USGS"
    DATASET = "DATASET"
    EMSC = "EMSC"
    GEOFON = "GEOFON"


@dataclass
class Earthquake:
    id: int
    time: datetime
    latitude: float
    longitude: float
    depth: float
    mag: float
    place: str
    source: EarthquakeSource
    month: int
    region: str
    category: EarthquakeCategory
