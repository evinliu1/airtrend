import sys

from sqlalchemy import text

from app.db import engine
from ingest import openaq

UPSERT = text("""
    INSERT INTO sensor_yearly (
        sensor_id, year, value, expected_count,
        observed_count, percent_complete, has_flags
    ) VALUES (
        :sensor_id, :year, :value, :expected_count,
        :observed_count, :percent_complete, :has_flags
    )
    ON CONFLICT (sensor_id, year) DO UPDATE SET
        value = EXCLUDED.value,
        expected_count = EXCLUDED.expected_count,
        observed_count = EXCLUDED.observed_count,
        percent_complete = EXCLUDED.percent_complete,
        has_flags = EXCLUDED.has_flags,
        ingested_at = now()
""")

PICK_SENSORS = text("""
    SELECT s.id
    FROM sensors s
    JOIN locations l on l.id = s.location_id
    WHERE s.parameter_name = :parameter AND l.is_mobile = false
    ORDER BY s.id
""")

def to_rows(sensor_id, results):
    rows = []
    for r in results:
        period = r.get("period") or {}
        start = (period.get("datetimeFrom") or {}).get("local")
        if not start:
            continue
        summary = r.get("summary") or {}
        coverage = r.get("coverage") or {}
        value = summary.get("avg", r.get("value"))
        if value is None:
            continue
        rows.append({
            "sensor_id": sensor_id,
            "year": int(start[:4]),
            "value": value,
            "expected_count": coverage.get("expectedCount"),
            "observed_count": coverage.get("observedCount"),
            "percent_complete": coverage.get("percentComplete"),
            "has_flags": bool((r.get("flagInfo") or {}).get("hasFlags")),
        })
    return rows

def run(parameter="pm25"):
    with engine.connect() as conn:
        sensor_ids = [r[0] for r in conn.execute(PICK_SENSORS, {"parameter": parameter})]

    print(f"{len(sensor_ids)} {parameter} sensors to fetch")

    done = written = failed = 0
    for sensor_id in sensor_ids:
        try:
            body = openaq.get(f"/sensors/{sensor_id}/years", {"limit": 100})
        except openaq.OpenAQError as exc:
            failed += 1
            print(f"sensor {sensor_id} failed: {exc}")
            continue

        rows = to_rows(sensor_id, body.get("results", []))
        if rows:
            with engine.begin() as conn:
                for row in rows:
                    conn.execute(UPSERT, row)
            written += len(rows)

        done += 1
        if done % 50 == 0:
            print(f"{done}/{len(sensor_ids)} sensors, {written} rows, {failed} failed")

    print(f"\ndone. {done} sensors, {written} rows, {failed} failed.")

if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "pm25")