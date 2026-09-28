import tempfile
import unittest
from pathlib import Path
from protocol.data_models import parse_sensor, parse_status
from storage.db import open_db, save_sensor_reading, save_device_status, sensor_history

class DataHardeningTests(unittest.TestCase):
    def test_validation_rejects_bad_values(self):
        with self.assertRaises(ValueError):
            parse_sensor({"timestamp":"bad","value":123})
        with self.assertRaises(ValueError):
            parse_status({"timestamp":"2026-01-01T00:00:00+00:00","battery_percent":101,"reservoir_units":10})

    def test_duplicates_are_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            con=open_db(Path(d)/"x.sqlite")
            try:
                r=parse_sensor({"timestamp":"2026-01-01T00:00:00+00:00","value":123})
                self.assertTrue(save_sensor_reading(con,r))
                self.assertFalse(save_sensor_reading(con,r))
                self.assertEqual(len(sensor_history(con)),1)
            finally:
                con.close()

if __name__ == "__main__":
    unittest.main()
