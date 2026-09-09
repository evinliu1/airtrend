# AirTrend

Air quality trends from OpenAQ (openaq.org)

## Setup Backend

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

## How the trend is computed

For each of the stations, we took the yearly pm25 average for each year where
OpenAQ reported at least 75% of expected hours. Then we fit a straight line
through those years. This is the slope of the trend in ug/m3 per year.
A positive slope means the air quality is worsening.

Stations with less than 5 qualifying years are excluded from this calculation.

### Why 75% and 5 years

One test station gave -0.271/yr when using all ten years
but also gave -0.783/yr using only the years above the 75% threshold. Earlier years had roughly
28-34% coverage which made their averages incomparable to later years in terms of
data quality

## Notes on data coverage

4,492 of the US pm25 5,838 sensors have yearly data (roughly 77%).
The remaining 1,346 don't have yearly records from OpenAQ, checked
directly against the API.

686 of the 14,665 yearly rows report 0% coverage and are excluded by
the 75% + 5 year rule.
