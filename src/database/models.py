from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Earthquake:
    id: int
    time: datetime
    latitude: float
    longitude: float
    depth: float
    mag: float
    place: str
    source: str
