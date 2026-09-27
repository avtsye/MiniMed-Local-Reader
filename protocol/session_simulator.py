"""Local read-only session state machine.

This module models application/session lifecycle only. It contains no pump
protocol, pairing logic, BLE writes, or therapy operations.
"""
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime, timezone

class SessionState(str, Enum):
    IDLE = "IDLE"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    TIMED_OUT = "TIMED_OUT"

@dataclass
class LocalSession:
    timeout_seconds: int = 30
    state: SessionState = SessionState.IDLE

    def open(self):
        if self.state is not SessionState.IDLE:
            raise RuntimeError(f"Cannot open session from {self.state.value}")
        self.state = SessionState.OPEN
        return self.state

    def close(self):
        if self.state is not SessionState.OPEN:
            raise RuntimeError(f"Cannot close session from {self.state.value}")
        self.state = SessionState.CLOSED
        return self.state

    def timeout(self):
        if self.state is not SessionState.OPEN:
            raise RuntimeError(f"Cannot timeout session from {self.state.value}")
        self.state = SessionState.TIMED_OUT
        return self.state

def record_event(con, event_type, payload):
    now = datetime.now(timezone.utc).isoformat()
    con.execute(
        "INSERT INTO pump_events(event_time,event_type,payload_json,source) VALUES(?,?,?,?)",
        (now, event_type, json.dumps(payload, ensure_ascii=False), "local-session-simulator"),
    )
    con.commit()

def run_demo(db_path):
    from storage.db import open_db
    con = open_db(db_path)
    session = LocalSession()
    try:
        record_event(con, "session_created", {"state": session.state.value})
        session.open()
        record_event(con, "session_opened", {"state": session.state.value})
        session.close()
        record_event(con, "session_closed", {"state": session.state.value})
        count = con.execute(
            "SELECT COUNT(*) FROM pump_events WHERE source='local-session-simulator'"
        ).fetchone()[0]
        return {
            "state": session.state.value,
            "events_in_db": count,
            "protocol_enabled": False,
            "pairing_enabled": False,
            "writes_enabled": False,
            "therapy_operations_enabled": False,
            "safe_mode": "local-session-simulator-only",
        }
    finally:
        con.close()
