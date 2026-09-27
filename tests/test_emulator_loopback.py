import tempfile
import unittest
from pathlib import Path
import sqlite3

from transport.emulator_loopback import run

class EmulatorLoopbackTests(unittest.TestCase):
    def test_full_loopback_flow(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db = Path(temp_dir) / "loopback.sqlite"
            result = run(db)
            self.assertTrue(result["loopback_completed"])
            self.assertTrue(result["expected_values_match"])
            self.assertFalse(result["bluetooth_radio_used"])
            self.assertEqual(result["events_this_run"], 5)

            con = sqlite3.connect(db)
            try:
                rows = con.execute(
                    "SELECT event_type FROM pump_events ORDER BY id"
                ).fetchall()
            finally:
                con.close()
            self.assertEqual([r[0] for r in rows], [
                "emulator_session_created",
                "emulator_session_opened",
                "emulator_gatt_read",
                "emulator_gatt_read",
                "emulator_session_closed",
            ])

if __name__ == "__main__":
    unittest.main()
