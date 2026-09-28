"""Import bridge for read-only exports produced by an external connector.

Accepted format is JSON Lines. Each row contains:
  channel: cgm_measurement | history_record | other label
  hex: hexadecimal bytes
Optional: timestamp, metadata.

This module never launches or controls the external connector.
"""
import json
from pathlib import Path
from protocol.raw_capture import RawPacketRecorder
from protocol.replay_pipeline import decode_replay

def import_connector_jsonl(source_path,capture_path):
    source=Path(source_path); recorder=RawPacketRecorder(capture_path); count=0
    with source.open("r",encoding="utf-8") as f:
        for number,line in enumerate(f,1):
            if not line.strip(): continue
            row=json.loads(line)
            if "channel" not in row or "hex" not in row:
                raise ValueError(f"line {number}: channel and hex are required")
            try:data=bytes.fromhex(row["hex"])
            except ValueError as e: raise ValueError(f"line {number}: invalid hex") from e
            recorder.record(row["channel"],data,row.get("metadata") or {})
            count+=1
    return {"imported":count,"decoded":decode_replay(capture_path)}

def export_contract():
    return {
      "format":"jsonl","required":["channel","hex"],
      "channels":["cgm_measurement","history_record"],
      "active_device_control":False
    }
