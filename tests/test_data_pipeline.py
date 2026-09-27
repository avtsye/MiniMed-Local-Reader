import tempfile
import unittest
from pathlib import Path

from protocol.data_pipeline import run

class DataPipelineTests(unittest.TestCase):
    def test_end_to_end_pipeline(self):
        with tempfile.TemporaryDirectory() as d:
            result = run(Path(d) / "pipeline.sqlite")
            self.assertTrue(result["pipeline_completed"])
            self.assertFalse(result["bluetooth_radio_used"])
            self.assertEqual(result["sensor"]["value"], 123.0)
            self.assertEqual(result["sensor"]["unit"], "mg/dL")
            self.assertEqual(result["status"]["battery_percent"], 80)
            self.assertEqual(result["status"]["reservoir_units"], 100.5)
            self.assertFalse(result["protocol_enabled"])
            self.assertFalse(result["writes_enabled"])

if __name__ == "__main__":
    unittest.main()
