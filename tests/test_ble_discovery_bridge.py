import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from protocol.ble_discovery_bridge import run
from storage.db import open_db

class BleDiscoveryBridgeTests(unittest.TestCase):
    @patch("protocol.ble_discovery_bridge.discover")
    def test_passive_results_are_logged_without_connection(self,mock_discover):
        mock_discover.return_value={"devices":[{"bluetooth_address":"ABC","rssi":-40,"local_name":"test","service_uuids":[]}]}
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"ble.sqlite"
            result=run(1,path)
            self.assertTrue(result["discovery_completed"])
            self.assertFalse(result["connection_attempted"])
            self.assertFalse(result["candidate_is_identified_pump"])
            con=open_db(path)
            try:
                count=con.execute("SELECT COUNT(*) FROM pump_events WHERE source='physical-ble-infrastructure'").fetchone()[0]
                self.assertGreaterEqual(count,4)
            finally: con.close()

if __name__=="__main__":
    unittest.main()
