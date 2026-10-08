"""Read-only parser for existing CareLink CSV exports.

No Bluetooth access. Patient identifiers and device serials are never returned.
Date and Time in this export are naive device-local wall-clock values.
"""
import csv
from collections import Counter
from datetime import datetime
from pathlib import Path

EXPECTED_DATE_FORMAT = "%d %m %Y %H:%M:%S"


def inspect_carelink_csv(path):
    path = Path(path)
    sections = []
    current = None
    measurements = 0
    invalid_dates = 0
    first_date = None
    last_date = None
    seen = set()
    repeated_times = 0

    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream)
        for row in reader:
            if len(row) < 3:
                continue
            if row[0].startswith("-------") and len(row) > 2 and row[2] in ("Pump", "Sensor"):
                current = {"kind": row[2], "rows": 0}
                sections.append(current)
                continue
            if row[0] == "Index":
                continue
            if current is None or not row[0].isdigit():
                continue
            current["rows"] += 1
            try:
                timestamp = datetime.strptime(row[1].strip() + " " + row[2].strip(), EXPECTED_DATE_FORMAT)
            except ValueError:
                invalid_dates += 1
                continue
            if timestamp in seen:
                repeated_times += 1
            seen.add(timestamp)
            if first_date is None or timestamp < first_date:
                first_date = timestamp
            if last_date is None or timestamp > last_date:
                last_date = timestamp
            if current["kind"] == "Sensor" and len(row) > 34 and row[34].strip():
                measurements += 1

    if not sections:
        raise ValueError("No supported CareLink Pump/Sensor sections found")
    return {
        "sections": sections,
        "sensor_measurement_rows": measurements,
        "invalid_date_rows": invalid_dates,
        "repeated_wall_clock_timestamps": repeated_times,
        "first_local_date": first_date.date().isoformat() if first_date else None,
        "last_local_date": last_date.date().isoformat() if last_date else None,
        "timestamps_have_timezone": False,
        "raw_rtc_available": False,
        "ngp_780g_timestamp_formula_verified": False,
    }
