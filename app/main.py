import os

from sqlalchemy import text
from fastapi import FastAPI
from dotenv import load_dotenv

from app.db import engine

load_dotenv()

app = FastAPI(title="AirTrend API")

@app.get("/api/health")
def health():
    with engine.connect() as conn:
        version = conn.execute(text("SELECT version()")).scalar()
        postgis = conn.execute(
            text("SELECT extname FROM pg_extension WHERE extname = 'postgis'")
        ).scalar()
    return {
        "status": "ok",
        "have_key": bool(os.getenv("OPENAQ_API_KEY")),
        "version": version.split(",")[0],
        "postgis": postgis or "NOT INSTALLED",
    }