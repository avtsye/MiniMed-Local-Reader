"""Synthetic implementation of the read-only data-source contract."""
from datetime import datetime, timezone
from datasource.base import ReadOnlyDataSource

class SyntheticDataSource(ReadOnlyDataSource):
    def __init__(self, sensor_value=123.0, battery_percent=80, reservoir_units=100.5):
        self.sensor_value=float(sensor_value)
        self.battery_percent=int(battery_percent)
        self.reservoir_units=float(reservoir_units)

    @property
    def source_name(self): return "synthetic-readonly-source"

    def read_sensor(self):
        return {"timestamp":datetime.now(timezone.utc).isoformat(),"value":self.sensor_value,"unit":"mg/dL"}

    def read_status(self):
        return {"timestamp":datetime.now(timezone.utc).isoformat(),
                "battery_percent":self.battery_percent,"reservoir_units":self.reservoir_units}
