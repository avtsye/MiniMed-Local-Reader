"""Internal read-only acquisition boundary.

This module accepts bytes that have already been obtained through an approved,
documented read-only interface. It deliberately exposes no device command,
pairing, write, or therapy-control API.
"""
from pathlib import Path

from protocol.history_ingest import ingest_history_record
from protocol.raw_capture import RawPacketRecorder

_ALLOWED_CHANNELS = {"history_record", "cgm_measurement", "device_status", "raw"}

class InternalReadOnlyAcquisition:
    def __init__(self, db_path="minimed_local.sqlite", capture_path=None):
        self.db_path = db_path
        if capture_path is None:
            capture_path = Path(db_path).with_suffix(".capture.jsonl")
        self.recorder = RawPacketRecorder(capture_path)

    @property
    def capabilities(self):
        return {
            "receive_bytes": True,
            "history": True,
            "writes": False,
            "commands": False,
            "pairing": False,
            "therapy_operations": False,
        }

    def accept_received(self, channel, data, metadata=None, reference_time=None):
        if channel not in _ALLOWED_CHANNELS:
            raise ValueError("unsupported read-only channel")
        raw = bytes(data)
        if not raw:
            raise ValueError("empty packet")
        captured = self.recorder.record(channel, raw, metadata)
        result = {
            "accepted": True,
            "channel": channel,
            "byte_count": len(raw),
            "capture": captured,
            "decoded": None,
            "writes_enabled": False,
            "commands_enabled": False,
            "pairing_enabled": False,
            "therapy_operations_enabled": False,
        }
        if channel == "history_record":
            result["decoded"] = ingest_history_record(
                raw, db_path=self.db_path, reference_time=reference_time
            )
        return result
