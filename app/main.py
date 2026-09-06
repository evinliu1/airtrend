import os

from typing import Optional
from sqlalchemy import text
from fastapi import FastAPI, HTTPException, Query
from dotenv import load_dotenv

from app.db import engine
from app.models import Location, LocationPage

load_dotenv()

app = FastAPI(title="AirTrend API")

SORTABLE = {"name", "country_code", "locality", "id"}

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

@app.get("/api/locations", response_model=LocationPage)
def list_locations(
    search: Optional[str] = None,
    country: Optional[str] = None,
    parameter: Optional[str] = None,
    sort_by: str = "name",
    order: str = "asc",
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
):
    if sort_by not in SORTABLE:
        raise HTTPException(400, f"cannot sort by {sort_by}")
    if order not in ("asc", "desc"):
        raise HTTPException(400, "order must be 'asc' or 'desc'")
    
    where = ["is_mobile = false"]
    params = {}

    if search:
        where.append("l.name ILIKE :search")
        params["search"] = f"%{search}%"
    if country:
        where.append("l.country_code = :country")
        params["country"] = country
    if parameter:
        where.append(
            "EXISTS (SELECT 1 FROM sensors s "
            "WHERE s.location_id = l.id AND s.parameter_name = :parameter)"
        )
        params["parameter"] = parameter
    
    where_sql = " AND ".join(where)

    count_sql = text(f"SELECT count(*) FROM locations l WHERE {where_sql}")

    rows_sql = text(f"""
        SELECT l.id, l.name, l.locality, l.country_code,
               l.provider_name, l.latitude, l.longitude
        FROM locations l
        WHERE {where_sql}
        ORDER BY l.{sort_by} {order.upper()}
        LIMIT :limit OFFSET :offset
    """)

    with engine.connect() as conn:
        total = conn.execute(count_sql, params).scalar()
        rows = conn.execute(
            rows_sql,
            {**params, "limit": per_page, "offset": (page - 1) * per_page},
        ).mappings().all()
    
    return LocationPage(
        data=[Location(**row) for row in rows],
        page=page,
        per_page=per_page,
        total=total,
        total_pages=(total + per_page - 1) // per_page
    )

@app.get("/api/locations/{location_id}", response_model=Location)
def get_location(location_id: int):
    sql = text("""
        SELECT id, name, locality, country_code,
               provider_name, latitude, longitude
        FROM locations
        where id = :id
    """)
    with engine.connect() as conn:
        row = conn.execute(sql, {"id": location_id}).mappings().first()
    if row is None:
        raise HTTPException(404, f"no location with id {location_id}")
    return Location(**row)

@app.get("/api/summary")
def summary():
    sql = text("""
        SELECT s.parameter_name,
               count(DISTINCT s.location_id) AS locations,
               count(*) AS sensors
        FROM sensors s
        JOIN locations l ON l.id = s.location_id
        WHERE l.is_mobile = false
        GROUP BY s.parameter_name
        ORDER BY sensors DESC
    """)
    with engine.connect() as conn:
        rows = conn.execute(sql).mappings().all()
    return {"parameters": [dict(r) for r in rows]}

@app.get("/api/locations/geojson")
def geojson():
    pass

