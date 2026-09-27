import tempfile
import unittest

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
        with tempfile.NamedTemporaryFile(suffix=".sqlite") as f:
            result = run_demo(f.name)
            self.assertEqual(result["state"], "CLOSED")
            self.assertEqual(result["events_in_db"], 3)
            self.assertFalse(result["protocol_enabled"])
            self.assertFalse(result["writes_enabled"])

if __name__ == "__main__":
    unittest.main()
