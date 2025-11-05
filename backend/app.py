from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from sqlmodel import select, desc
from .database import init_db, get_session
from .models import TrafficReading, SignalDecision
from .optimizer import decide_green_seconds
from .security import require_api_key

app = FastAPI(title="Smart Traffic Cloud API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReadingIn(BaseModel):
    timestamp: datetime
    junction_id: str
    vehicle_count: int
    avg_speed_kmh: float

@app.on_event("startup")
def on_startup():
    init_db()

@app.post("/ingest", dependencies=[Depends(require_api_key)])
def ingest_reading(payload: ReadingIn, session=Depends(get_session)):
    reading = TrafficReading(**payload.dict())
    session.add(reading)

    green, reason = decide_green_seconds(
        payload.vehicle_count, payload.avg_speed_kmh
    )
    decision = SignalDecision(
        timestamp=payload.timestamp,
        junction_id=payload.junction_id,
        green_seconds=green,
        reason=reason
    )
    session.add(decision)
    session.commit()
    return {"stored": True, "decision": {"green_seconds": green, "reason": reason}}

@app.get("/readings", response_model=List[TrafficReading])
def get_readings(
    junction_id: Optional[str] = None,
    limit: int = Query(200, le=2000),
    session=Depends(get_session)
):
    stmt = select(TrafficReading).order_by(desc(TrafficReading.timestamp)).limit(limit)
    if junction_id:
        stmt = stmt.where(TrafficReading.junction_id == junction_id)
    return list(session.exec(stmt))

@app.get("/decisions", response_model=List[SignalDecision])
def get_decisions(
    junction_id: Optional[str] = None,
    limit: int = Query(200, le=2000),
    session=Depends(get_session)
):
    stmt = select(SignalDecision).order_by(desc(SignalDecision.timestamp)).limit(limit)
    if junction_id:
        stmt = stmt.where(SignalDecision.junction_id == junction_id)
    return list(session.exec(stmt))

@app.get("/health")
def health():
    return {"status": "ok"}
