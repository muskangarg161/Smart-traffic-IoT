from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class TrafficReading(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime
    junction_id: str
    vehicle_count: int
    avg_speed_kmh: float

class SignalDecision(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime
    junction_id: str
    green_seconds: int
    reason: str
