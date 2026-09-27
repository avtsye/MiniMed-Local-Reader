import tempfile
import unittest
from pathlib import Path

from protocol.data_models import parse_sensor, parse_status
from storage.db import open_db, save_sensor_reading, save_device_status

class DataLayerTests(unittest.TestCase):
    def test_parse_store_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            con = open_db(Path(d) / "data.sqlite")
            try:
                sensor = parse_sensor({"timestamp":"2026-01-01T12:00:00Z","value":123})
                status = parse_status({"timestamp":"2026-01-01T12:00:00Z","battery_percent":80,"reservoir_units":100.5})
                save_sensor_reading(con, sensor)
                save_device_status(con, status)
                self.assertEqual(con.execute("SELECT value,unit FROM sensor_readings").fetchone(), (123.0,"mg/dL"))
                self.assertEqual(con.execute("SELECT battery_percent,reservoir_units FROM device_status").fetchone(), (80,100.5))
            finally:
                con.close()

if __name__ == "__main__":
    unittest.main()
