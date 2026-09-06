# AirTrend

Air quality trends from OpenAQ (openaq.org)

## Setup

1. copy .env.example to .env, add your OpenAQ key
2. docker compose up -d
3. Get-Content schema.sql | docker compose exec -T db psql -U airtrend -d airtrend
4. pip install -r requirements.txt
5. python -m ingest.locations <country_code>
6. uvicorn app.main:app --reload

## Endpoints

GET /api/health
GET /api/locations
GET /api/locations/{location_id}
GET /api/summary
GET /api/geojson
