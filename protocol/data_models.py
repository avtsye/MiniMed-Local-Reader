"""Read-only normalized models and format validation for simulated data."""
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

def _timestamp(value):
    text = str(value).strip()
    if not text:
        raise ValueError("timestamp is required")
    datetime.fromisoformat(text.replace("Z", "+00:00"))
    return text

def parse_sensor(payload):
    if not isinstance(payload, dict):
        raise ValueError("sensor payload must be an object")
    value = float(payload["value"])
    if value <= 0 or value > 1000:
        raise ValueError("sensor value failed format bounds")
    unit = str(payload.get("unit", "mg/dL")).strip()
    if not unit:
        raise ValueError("unit is required")
    return SensorReading(_timestamp(payload["timestamp"]), value, unit)

def parse_status(payload):
    if not isinstance(payload, dict):
        raise ValueError("status payload must be an object")
    battery = int(payload["battery_percent"])
    reservoir = float(payload["reservoir_units"])
    if not 0 <= battery <= 100:
        raise ValueError("battery_percent must be 0..100")
    if reservoir < 0:
        raise ValueError("reservoir_units cannot be negative")
    return DeviceStatus(_timestamp(payload["timestamp"]), battery, reservoir)

def to_dict(model):
    return asdict(model)
