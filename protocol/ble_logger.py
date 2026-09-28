"""Local structured log for BLE infrastructure events."""
import json
from datetime import datetime, timezone

def log_event(con, event_type, payload=None):
    con.execute(
        "INSERT INTO pump_events(event_time,event_type,payload_json,source) VALUES(?,?,?,?)",
        (datetime.now(timezone.utc).isoformat(), event_type,
         json.dumps(payload or {}, ensure_ascii=False), "physical-ble-infrastructure"),
    )
    con.commit()
