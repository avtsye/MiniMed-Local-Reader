import tempfile
import unittest
from pathlib import Path
from datasource.carelink_csv import inspect_carelink_csv


class CareLinkCsvTests(unittest.TestCase):
    def test_sections_and_no_identifiers(self):
        sample = (
            "Last Name,First Name,Patient ID\n"
            "-------,MiniMed 780G,Pump\n"
            "Index,Date,Time\n"
            "0,08 10 2026,11:20:09\n"
            "-------,MiniMed 780G,Sensor\n"
            "Index,Date,Time," + ",".join([""] * 31) + ",Sensor Glucose (mg/dL)\n"
            "0,08 10 2026,11:20:09," + ",".join([""] * 31) + ",120\n"
        )
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "export.csv"
            path.write_text(sample, encoding="utf-8")
            result = inspect_carelink_csv(path)
        self.assertEqual(result["sections"][0]["kind"], "Pump")
        self.assertEqual(result["sections"][1]["kind"], "Sensor")
        self.assertEqual(result["repeated_wall_clock_timestamps"], 1)
        self.assertFalse(result["raw_rtc_available"])
        self.assertNotIn("Patient ID", str(result))

    def test_invalid_date(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "export.csv"
            path.write_text("-------,Device,Pump\nIndex,Date,Time\n0,invalid,invalid\n", encoding="utf-8")
            result = inspect_carelink_csv(path)
        self.assertEqual(result["invalid_date_rows"], 1)


if __name__ == "__main__":
    unittest.main()
