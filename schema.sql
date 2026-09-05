CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS locations(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    locality TEXT,
    timezone TEXT NOT NULL,
    country_code TEXT NOT NULL,
    country_name TEXT,
    provider_id INTEGER,
    provider_name TEXT,
    is_mobile BOOLEAN NOT NULL DEFAULT FALSE,
    is_monitor BOOLEAN NOT NULL DEFAULT FALSE,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    geom geometry(Point, 4326),
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_locations_country ON locations (country_code);

CREATE INDEX IF NOT EXISTS idx_locations_geom ON locations USING GIST (geom);

CREATE TABLE IF NOT EXISTS sensors (
    id INTEGER PRIMARY KEY,
    location_id INTEGER NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    parameter_id INTEGER NOT NULL,
    parameter_name TEXT NOT NULL,
    units TEXT,
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_sensors_location ON sensors (location_id);

CREATE INDEX IF NOT EXISTS idx_sensors_parameter ON sensors (parameter_name);