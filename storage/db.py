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
"""

def open_db(path="minimed_local.sqlite"):
    path = Path(path)
    con = sqlite3.connect(path)
    con.executescript(SCHEMA)
    return con
