import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS pump_events (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 event_time TEXT,
 event_type TEXT NOT NULL,
 payload_json TEXT NOT NULL,
 source TEXT NOT NULL DEFAULT 'local'
);
CREATE INDEX IF NOT EXISTS idx_events_time ON pump_events(event_time);
CREATE INDEX IF NOT EXISTS idx_events_type ON pump_events(event_type);

CREATE TABLE IF NOT EXISTS sensor_readings (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 event_time TEXT NOT NULL,
 value REAL NOT NULL,
 unit TEXT NOT NULL,
 source TEXT NOT NULL DEFAULT 'simulator'
);
CREATE INDEX IF NOT EXISTS idx_sensor_time ON sensor_readings(event_time);

CREATE TABLE IF NOT EXISTS device_status (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 event_time TEXT NOT NULL,
 battery_percent INTEGER NOT NULL,
 reservoir_units REAL NOT NULL,
 source TEXT NOT NULL DEFAULT 'simulator'
);
CREATE INDEX IF NOT EXISTS idx_status_time ON device_status(event_time);
"""

def open_db(path="minimed_local.sqlite"):
    path = Path(path)
    con = sqlite3.connect(path)
    con.executescript(SCHEMA)
    return con


def save_sensor_reading(con, reading, source="simulator"):
    con.execute(
        "INSERT INTO sensor_readings(event_time,value,unit,source) VALUES(?,?,?,?)",
        (reading.timestamp, reading.value, reading.unit, source),
    )
    con.commit()

def save_device_status(con, status, source="simulator"):
    con.execute(
        "INSERT INTO device_status(event_time,battery_percent,reservoir_units,source) VALUES(?,?,?,?)",
        (status.timestamp, status.battery_percent, status.reservoir_units, source),
    )
    con.commit()
