import tempfile
import unittest
from pathlib import Path
from protocol.ble_state import BleSessionState, BleState
from protocol.physical_ble_guard import block_write, block_pairing, BleWriteBlocked, PairingBlocked, safety_status
from protocol.ble_logger import log_event
from storage.db import open_db

class PhysicalBleInfrastructureTests(unittest.TestCase):
    def test_readonly_lifecycle(self):
        s=BleSessionState()
        s.transition(BleState.DISCOVERING)
        s.transition(BleState.CANDIDATE_FOUND,address="TEST")
        s.transition(BleState.CONNECTING)
        s.transition(BleState.CONNECTED_READ_ONLY)
        s.transition(BleState.DISCONNECTED)
        self.assertEqual(s.state,BleState.DISCONNECTED)

    def test_invalid_transition_blocked(self):
        with self.assertRaises(RuntimeError):
            BleSessionState().transition(BleState.CONNECTED_READ_ONLY)

    def test_write_and_pairing_are_hard_blocked(self):
        with self.assertRaises(BleWriteBlocked): block_write(b"x")
        with self.assertRaises(PairingBlocked): block_pairing()
        status=safety_status()
        self.assertFalse(status["gatt_writes_enabled"])
        self.assertFalse(status["pairing_enabled"])

    def test_event_logging(self):
        with tempfile.TemporaryDirectory() as d:
            con=open_db(Path(d)/"ble.sqlite")
            try:
                log_event(con,"ble_infrastructure_test",{"ok":True})
                row=con.execute("SELECT source FROM pump_events WHERE event_type='ble_infrastructure_test'").fetchone()
                self.assertEqual(row[0],"physical-ble-infrastructure")
            finally: con.close()

if __name__=="__main__":
    unittest.main()
