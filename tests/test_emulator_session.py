import tempfile
import unittest
from pathlib import Path

from protocol.emulator_session import EmulatorSessionLog

class EmulatorSessionIntegrationTests(unittest.TestCase):
    def test_lifecycle_and_read_are_persisted(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db = Path(temp_dir) / "integration.sqlite"
            log = EmulatorSessionLog(db)
            try:
                log.start("test-service")
                log.record_read("test-characteristic")
                log.finish()
                self.assertEqual(log.event_count(), 4)
                rows = log.con.execute(
                    "SELECT event_type FROM pump_events "
                    "WHERE event_type LIKE 'emulator_%' ORDER BY id"
                ).fetchall()
                self.assertEqual([r[0] for r in rows], [
                    "emulator_session_created",
                    "emulator_session_opened",
                    "emulator_gatt_read",
                    "emulator_session_closed",
                ])
            finally:
                log.close_db()

if __name__ == "__main__":
    unittest.main()
