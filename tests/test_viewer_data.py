import tempfile
import unittest
from pathlib import Path

from storage.db import open_db

class ViewerDataContractTests(unittest.TestCase):
    def test_viewer_queries_have_required_tables(self):
        with tempfile.TemporaryDirectory() as d:
            con = open_db(Path(d) / "viewer.sqlite")
            try:
                sensor_cols = {r[1] for r in con.execute("PRAGMA table_info(sensor_readings)")}
                status_cols = {r[1] for r in con.execute("PRAGMA table_info(device_status)")}
                self.assertTrue({"event_time","value","unit","source"} <= sensor_cols)
                self.assertTrue({"battery_percent","reservoir_units"} <= status_cols)
            finally:
                con.close()

if __name__ == "__main__":
    unittest.main()
