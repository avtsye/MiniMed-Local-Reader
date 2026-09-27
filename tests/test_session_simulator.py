import tempfile
import unittest
from pathlib import Path

from protocol.session_simulator import LocalSession, SessionState, run_demo


class SessionSimulatorTests(unittest.TestCase):
    def test_open_close(self):
        s = LocalSession()
        self.assertEqual(s.state, SessionState.IDLE)
        self.assertEqual(s.open(), SessionState.OPEN)
        self.assertEqual(s.close(), SessionState.CLOSED)

    def test_timeout(self):
        s = LocalSession()
        s.open()
        self.assertEqual(s.timeout(), SessionState.TIMED_OUT)

    def test_invalid_transition(self):
        s = LocalSession()
        with self.assertRaises(RuntimeError):
            s.close()

    def test_demo_persists_events(self):
        # On Windows, NamedTemporaryFile keeps an open handle that can prevent
        # sqlite3 from reopening the same path. Use a temporary directory and
        # let SQLite create its own database file instead.
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "session_test.sqlite"
            result = run_demo(db_path)
            self.assertEqual(result["state"], "CLOSED")
            self.assertEqual(result["events_in_db"], 3)
            self.assertFalse(result["protocol_enabled"])
            self.assertFalse(result["writes_enabled"])
            self.assertTrue(db_path.exists())


if __name__ == "__main__":
    unittest.main()
