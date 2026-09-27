"""Read-only normalized data models for simulated device data."""
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass(frozen=True)
class SensorReading:
    timestamp: str
    value: float
    unit: str = "mg/dL"

@dataclass(frozen=True)
class DeviceStatus:
    timestamp: str
    battery_percent: int
    reservoir_units: float

def parse_sensor(payload):
    return SensorReading(
        timestamp=str(payload["timestamp"]),
        value=float(payload["value"]),
        unit=str(payload.get("unit", "mg/dL")),
    )

def parse_status(payload):
    return DeviceStatus(
        timestamp=str(payload["timestamp"]),
        battery_percent=int(payload["battery_percent"]),
        reservoir_units=float(payload["reservoir_units"]),
    )

def to_dict(model):
    return asdict(model)
