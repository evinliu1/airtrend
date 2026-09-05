import sys

from sqlalchemy import text

from app.db import engine
from ingest import openaq

UPSERT_LOCATION = text("""
    INSERT INTO locations(
        id, name, locality, timezone, country_code, country_name,
        provider_id, provider_name, is_mobile, is_monitor,
        latitude, longitude, geom
    ) VALUES (
        :id, :name, :locality, :timezone, :country_code, :country_name,
        :provider_id, :provider_name, :is_mobile, :is_monitor,
        :latitude, :longitude,
        ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)
    )
    ON CONFLICT (id) DO UPDATE SET
        name = EXCLUDED.name,
        locality = EXCLUDED.locality,
        timezone = EXCLUDED.timezone,
        country_code = EXCLUDED.country_code,
        country_name = EXCLUDED.country_name,
        provider_id = EXCLUDED.provider_id,
        provider_name = EXCLUDED.provider_name,
        is_mobile = EXCLUDED.is_mobile,
        is_monitor = EXCLUDED.is_monitor,
        latitude = EXCLUDED.latitude,
        longitude = EXCLUDED.longitude,
        geom = EXCLUDED.geom,
        last_seen_at = now()
""")

UPSERT_SENSOR = text("""
    INSERT INTO sensors (
        id, location_id, parameter_id, parameter_name, units
    ) VALUES (
        :id, :location_id, :parameter_id, :parameter_name, :units
    )
    ON CONFLICT (id) DO UPDATE SET
        location_id = EXCLUDED.location_id,
        parameter_id = EXCLUDED.parameter_id,
        parameter_name = EXCLUDED.parameter_name,
        units = EXCLUDED.units,
        last_seen_at = now()
""")

def to_location_row(location):
    """
        Flatten one OPENAQ location object into columns our table has.
    """
    coords = location.get("coordinates") or {}
    country = location.get("country") or {}
    provider = location.get("provider") or {}
    return {
        "id": location["id"],
        "name": location.get("name") or "unknown",
        "locality": location.get("locality"),
        "timezone": location.get("timezone") or "UTC",
        "country_code": country.get("code") or "??",
        "country_name": country.get("name"),
        "provider_id": provider.get("id"),
        "provider_name": provider.get("name"),
        "is_mobile": bool(location.get("isMobile")),
        "is_monitor": bool(location.get("isMonitor")),
        "latitude": coords.get("latitude"),
        "longitude": coords.get("longitude"),
    }

def to_sensor_rows(location):
    """
        One row per sensor attached to this location.
    """
    rows = []
    for sensor in location.get("sensors") or []:
        parameter = sensor.get("parameter") or {}
        rows.append({
            "id": sensor["id"],
            "location_id": location["id"],
            "parameter_id": parameter.get("id"),
            "parameter_name": parameter.get("name") or "unknown",
            "units": parameter.get("units"),
        })
    return rows

def run(country_id, batch_size=200):
    kept = skipped = sensors_written = 0
    batch = []

    def flush(rows):
        nonlocal sensors_written
        if not rows:
            return
        with engine.begin() as conn:
            for loc_row, sensor_rows in rows:
                conn.execute(UPSERT_LOCATION, loc_row)
                for sensor_row in sensor_rows:
                    conn.execute(UPSERT_SENSOR, sensor_row)
                    sensors_written += 1

    for loc in openaq.paginate("/locations", {"countries_id": country_id}):
        if loc.get("isMobile"):
            skipped += 1
            continue
        if not (loc.get("coordinates") or {}).get("latitude"):
            skipped += 1
            continue

        batch.append((to_location_row(loc), to_sensor_rows(loc)))
        kept += 1

        if len(batch) >= batch_size:
            flush(batch)
            batch = []
            print(f"committed {kept} locations so far")
        
    flush(batch)
    print(f"\ndone. {kept} locations, {sensors_written} sensors, {skipped} skipped.")

if __name__ == "__main__":
    country = int(sys.argv[1]) if len(sys.argv) > 1 else 155
    run(country)