from __future__ import annotations

from collections import namedtuple
from dataclasses import asdict, dataclass
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

    def to_dict(
        self,
    ) -> dict[
        str, int | datetime | float | str | EarthquakeSource | EarthquakeCategory
    ]:
        return asdict(self)

    def to_record_namedtuple(self) -> tuple:
        Record = namedtuple(
            "Record",
            [
                "id",
                "time",
                "latitude",
                "longitude",
                "depth",
                "mag",
                "place",
                "source",
                "month",
                "region",
                "category",
            ],
        )
        return Record(**self.to_dict())
