from fastapi import FastAPI
import os
from sqlmodel import Column,DateTime,Field,SQLModel,create_engine,Session,func,select
from typing import Optional
from datetime import datetime
import httpx
from sqlalchemy import text

DB_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/ai_triage_system")
engine = create_engine(DB_URL)

class LogEntry(SQLModel, table=True):
    __tablename__ = 'log_entries'

    id: Optional[int] = Field(default=None, primary_key=True)
    message: str
    category: str = "Pending"
    is_urgent: bool = False
    created_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=True))


app = FastAPI()

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.post('/logs')
async def create_log(log: LogEntry):
    with Session(engine) as session:
        session.add(log)
        session.commit()
        session.refresh(log)

    n8n_url = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook-test/triage-trigger")
    async with httpx.AsyncClient() as client:
        await client.post(n8n_url, json={'id': log.id, 'message': log.message})

    return {"status": "Database Updated", "log_id": log.id}


@app.get('/stats')
async def get_stats():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT category, COUNT(*) as count FROM log_entries GROUP BY category"))
        urgent = conn.execute(text("SELECT is_urgent, COUNT(*) as count FROM log_entries GROUP BY is_urgent"))
        dist = {row.category: row.count for row in res.all()}
        urgency = {str(row.is_urgent): row.count for row in urgent.all()}
    return {
        "distribution": dist,
        "urgency": urgency
    }
