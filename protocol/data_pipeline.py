"""End-to-end simulated read-only data pipeline."""
from datetime import datetime, timezone

from protocol.data_models import parse_sensor, parse_status
from storage.db import open_db, save_sensor_reading, save_device_status
from transport.emulator_loopback import run as run_loopback

def run(db_path):
    loopback = run_loopback(db_path)
    if not loopback.get("loopback_completed"):
        return {"pipeline_completed": False, "reason": "loopback failed"}

    now = datetime.now(timezone.utc).isoformat()
    sensor = parse_sensor({"timestamp": now, "value": 123, "unit": "mg/dL"})
    status = parse_status({
        "timestamp": now,
        "battery_percent": 80,
        "reservoir_units": 100.5,
    })

    con = open_db(db_path)
    try:
        save_sensor_reading(con, sensor, source="pipeline-simulator")
        save_device_status(con, status, source="pipeline-simulator")
        sensor_row = con.execute(
            "SELECT event_time,value,unit FROM sensor_readings "
            "WHERE source='pipeline-simulator' ORDER BY id DESC LIMIT 1"
        ).fetchone()
        status_row = con.execute(
            "SELECT event_time,battery_percent,reservoir_units FROM device_status "
            "WHERE source='pipeline-simulator' ORDER BY id DESC LIMIT 1"
        ).fetchone()
    finally:
        con.close()

    return {
        "pipeline_completed": True,
        "transport": "software-loopback",
        "bluetooth_radio_used": False,
        "sensor": {"timestamp": sensor_row[0], "value": sensor_row[1], "unit": sensor_row[2]},
        "status": {
            "timestamp": status_row[0],
            "battery_percent": status_row[1],
            "reservoir_units": status_row[2],
        },
        "protocol_enabled": False,
        "pairing_started": False,
        "writes_enabled": False,
        "therapy_operations_enabled": False,
        "safe_mode": "simulated-data-pipeline-only",
    }
