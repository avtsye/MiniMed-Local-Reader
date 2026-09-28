"""Replay-backed read-only source for decoded CGM packets."""
from datetime import datetime, timezone
from datasource.base import ReadOnlyDataSource
from protocol.raw_capture import replay
from protocol.cgm_decoder import decode_cgm_measurement

class ReplayCGMDataSource(ReadOnlyDataSource):
    def __init__(self,path,battery_percent=0,reservoir_units=0.0):
        self.path=path; self.battery_percent=battery_percent; self.reservoir_units=reservoir_units
    @property
    def source_name(self): return "raw-replay-readonly"
    def read_sensor(self):
        rows=list(replay(self.path))
        cgm=[x for x in rows if x["channel"]=="cgm_measurement"]
        if not cgm: raise ValueError("No CGM measurement packet in replay")
        decoded=decode_cgm_measurement(cgm[-1]["data"],bool(cgm[-1].get("metadata",{}).get("use_crc",False)))
        return {"timestamp":cgm[-1]["timestamp"],"value":decoded["glucose"],"unit":"mg/dL"}
    def read_status(self):
        return {"timestamp":datetime.now(timezone.utc).isoformat(),
                "battery_percent":self.battery_percent,"reservoir_units":self.reservoir_units}
