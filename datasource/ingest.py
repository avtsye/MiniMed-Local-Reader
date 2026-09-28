"""Validated ingest pipeline for read-only data sources."""
from protocol.data_models import parse_sensor, parse_status
from storage.db import open_db, save_sensor_reading, save_device_status

def ingest_once(source, db_path="minimed_local.sqlite"):
    caps=source.capabilities()
    if caps.get("writes") or caps.get("commands") or caps.get("pairing") or caps.get("therapy_operations"):
        raise RuntimeError("Unsafe data source capabilities rejected")
    sensor=parse_sensor(source.read_sensor())
    status=parse_status(source.read_status())
    con=open_db(db_path)
    try:
        sensor_inserted=save_sensor_reading(con,sensor,source=source.source_name)
        status_inserted=save_device_status(con,status,source=source.source_name)
    finally: con.close()
    return {
        "ingest_completed":True,"source":source.source_name,
        "sensor_inserted":sensor_inserted,"status_inserted":status_inserted,
        "writes_enabled":False,"commands_enabled":False,
        "pairing_enabled":False,"therapy_operations_enabled":False,
    }
