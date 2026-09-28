import json
import tempfile
import unittest
from pathlib import Path
from protocol.ble_classifier import classify
from protocol.ble_logger import log_event
from storage.db import open_db

class BleClassifierTests(unittest.TestCase):
    def test_descriptive_evidence_only(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"c.sqlite"; con=open_db(path)
            try:
                log_event(con,"ble_advertisement_observed",{
                    "bluetooth_address":"ABC","rssi":-40,"local_name":"X",
                    "service_uuids":["uuid"],"manufacturer_data":[{"company_id":7,"data_hex":"AA"}],
                    "data_sections":[{"data_type":22,"data_hex":"BB"}]})
            finally: con.close()
            result=classify(path)
            self.assertEqual(result["candidate_count"],1)
            c=result["candidates"][0]
            self.assertFalse(c["identified_as_pump"])
            self.assertEqual(c["manufacturer_company_ids"],[7])
            self.assertEqual(c["data_types"],[22])
            self.assertFalse(result["connection_attempted"])

if __name__=="__main__": unittest.main()
