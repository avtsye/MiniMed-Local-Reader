"""Continuous local simulator.

Generates synthetic display data only. No Bluetooth, pump protocol, pairing,
writes, therapy controls, or treatment logic are used.
"""
import time
from datetime import datetime, timezone

from protocol.data_models import parse_sensor, parse_status
from storage.db import open_db, save_sensor_reading, save_device_status

def _sample(index):
    # Deterministic synthetic waveform; values are test fixtures, not patient data.
    cycle = (0, 3, 6, 9, 6, 3, 0, -3, -6, -9, -6, -3)
    value = 123 + cycle[index % len(cycle)]
    battery = max(0, 80 - index // 100)
    reservoir = max(0.0, 100.5 - index * 0.05)
    return value, battery, reservoir

def run(db_path="minimed_local.sqlite", seconds=60, interval=2.0, stress_count=0):
    if seconds < 1 or seconds > 86400:
        raise ValueError("seconds must be between 1 and 86400")
    if interval <= 0:
        raise ValueError("interval must be positive")
    if stress_count < 0 or stress_count > 100000:
        raise ValueError("stress_count must be 0..100000")

    con = open_db(db_path)
    inserted = 0
    skipped_missing = 0
    try:
        target = stress_count if stress_count else None
        started = time.monotonic()
        index = 0
        while True:
            if target is not None:
                if index >= target:
                    break
            elif time.monotonic() - started >= seconds:
                break

            # Every 17th sample simulates a missing read without inventing a value.
            if index and index % 17 == 0:
                skipped_missing += 1
            else:
                value, battery, reservoir = _sample(index)
                timestamp = datetime.now(timezone.utc).isoformat()
                sensor = parse_sensor({"timestamp": timestamp, "value": value, "unit": "mg/dL"})
                status = parse_status({
                    "timestamp": timestamp,
                    "battery_percent": battery,
                    "reservoir_units": reservoir,
                })
                save_sensor_reading(con, sensor, source="continuous-simulator")
                save_device_status(con, status, source="continuous-simulator")
                inserted += 1

            index += 1
            if target is None:
                time.sleep(interval)

        return {
            "simulation_completed": True,
            "generated_samples": index,
            "inserted_samples": inserted,
            "simulated_missing_reads": skipped_missing,
            "bluetooth_radio_used": False,
            "pump_connected": False,
            "protocol_enabled": False,
            "pairing_started": False,
            "writes_enabled": False,
            "therapy_operations_enabled": False,
            "safe_mode": "continuous-synthetic-data-only",
        }
    finally:
        con.close()
