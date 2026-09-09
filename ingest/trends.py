import sys

from sqlalchemy import text

from app.db import engine

COMPUTE = text(""" 
    WITH location_year AS (
        SELECT  l.id AS location_id,
                s.parameter_name,
                y.year,
                avg(y.value) as value
        FROM sensor_yearly y
        JOIN sensors s ON s.id = y.sensor_id
        JOIN locations l ON l.id = s.location_id
        WHERE y.percent_complete >= :min_coverage AND l.is_mobile = false
        GROUP BY l.id, s.parameter_name, y.year
    )
    INSERT INTO station_trends (
        location_id, parameter_name, slope, r2, mean_value,
        years_used, first_year, last_year, min_coverage
    )
    SELECT  location_id,
            parameter_name,
            regr_slope(value, year),
            regr_r2(value, year),
            avg(value),
            count(*),
            min(year),
            max(year),
            :min_coverage
    FROM location_year
    GROUP BY location_id, parameter_name
    HAVING count(*) >= :min_years
    ON CONFLICT (location_id, parameter_name) DO UPDATE SET
        slope = EXCLUDED.slope,
        r2 = EXCLUDED.r2,
        mean_value = EXCLUDED.mean_value,
        years_used = EXCLUDED.years_used,
        first_year = EXCLUDED.first_year,
        last_year = EXCLUDED.last_year,
        min_coverage = EXCLUDED.min_coverage,
        computed_at = now()
""")
CLEAR_OUT = text("""
    DELETE FROM station_trends WHERE parameter_name = 'pm25'
""")

def run(min_coverage=75.0, min_years=5):
    with engine.begin() as conn:
        conn.execute(CLEAR_OUT)
        result = conn.execute(
            COMPUTE, {"min_coverage": min_coverage, "min_years": min_years}
        )
    print(f"coverage >= {min_coverage}, at least {min_years} years")
    print(f"{result.rowcount} stations trends written")

if __name__ == "__main__":
    cov = float(sys.argv[1]) if len(sys.argv) > 1 else 75.0
    yrs = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    run(cov, yrs)