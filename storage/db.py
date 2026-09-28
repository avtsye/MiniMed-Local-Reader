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
CREATE UNIQUE INDEX IF NOT EXISTS uq_sensor_reading
 ON sensor_readings(event_time,value,unit,source);

CREATE TABLE IF NOT EXISTS device_status (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 event_time TEXT NOT NULL,
 battery_percent INTEGER NOT NULL,
 reservoir_units REAL NOT NULL,
 source TEXT NOT NULL DEFAULT 'simulator'
);
CREATE INDEX IF NOT EXISTS idx_status_time ON device_status(event_time);
CREATE UNIQUE INDEX IF NOT EXISTS uq_device_status
 ON device_status(event_time,battery_percent,reservoir_units,source);
"""

def open_db(path="minimed_local.sqlite"):
    con = sqlite3.connect(Path(path))
    con.executescript(SCHEMA)
    return con

def save_sensor_reading(con, reading, source="simulator"):
    cur = con.execute(
        "INSERT OR IGNORE INTO sensor_readings(event_time,value,unit,source) VALUES(?,?,?,?)",
        (reading.timestamp, reading.value, reading.unit, source),
    )
    con.commit()
    return cur.rowcount == 1

def save_device_status(con, status, source="simulator"):
    cur = con.execute(
        "INSERT OR IGNORE INTO device_status(event_time,battery_percent,reservoir_units,source) VALUES(?,?,?,?,?)"
        .replace("VALUES(?,?,?,?,?)", "VALUES(?,?,?,?)"),
        (status.timestamp, status.battery_percent, status.reservoir_units, source),
    )
    con.commit()
    return cur.rowcount == 1

def latest_sensor(con):
    return con.execute(
        "SELECT event_time,value,unit,source FROM sensor_readings ORDER BY event_time DESC,id DESC LIMIT 1"
    ).fetchone()

def latest_status(con):
    return con.execute(
        "SELECT event_time,battery_percent,reservoir_units,source FROM device_status ORDER BY event_time DESC,id DESC LIMIT 1"
    ).fetchone()

def sensor_history(con, limit=100, since=None):
    limit = max(1, min(int(limit), 10000))
    if since:
        return con.execute(
            "SELECT event_time,value,unit,source FROM sensor_readings WHERE event_time>=? ORDER BY event_time DESC,id DESC LIMIT ?",
            (since, limit),
        ).fetchall()
    return con.execute(
        "SELECT event_time,value,unit,source FROM sensor_readings ORDER BY event_time DESC,id DESC LIMIT ?",
        (limit,),
    ).fetchall()
