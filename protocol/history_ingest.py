"""Offline decoded-history ingestion.

Only already-captured history bytes are accepted. No device transport is used.
"""
from datetime import datetime,timezone,timedelta
from protocol.history_decoder import decode_known_history_record
from protocol.data_models import parse_sensor
from storage.db import open_db,save_sensor_reading

def ingest_history_record(data,db_path="minimed_local.sqlite",reference_time=None):
    record=decode_known_history_record(data)
    if record["event_type"]!=0xF00C or not record["decoded"]:
        return {"stored":False,"event_name":record["event_name"]}
    sg=record["decoded"]
    if sg["sg_value"] is None:
        return {"stored":False,"event_name":record["event_name"],"sg_state":sg["sg_state"]}
    base=reference_time or datetime.now(timezone.utc)
    when=base+timedelta(minutes=sg["time_offset_minutes"])
    reading=parse_sensor({"timestamp":when.isoformat(),"value":sg["sg_value"],"unit":"mg/dL"})
    con=open_db(db_path)
    try: stored=save_sensor_reading(con,reading,source="history-replay-readonly")
    finally: con.close()
    return {"stored":stored,"event_name":record["event_name"],"sensor_value":sg["sg_value"]}
