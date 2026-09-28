import tempfile
import unittest
from datetime import datetime,timezone
from pathlib import Path
from protocol.history_decoder import decode_sg_measurement_payload,decode_known_history_record
from protocol.history_ingest import ingest_history_record
from transport.external_readonly_sink import ExternalReadOnlyByteSink
from storage.db import open_db

class HistorySgTests(unittest.TestCase):
    def test_sg_decode_and_store(self):
        payload=(5).to_bytes(2,"little",signed=True)+(123).to_bytes(2,"little")+(42).to_bytes(2,"little")+(-2).to_bytes(2,"little",signed=True)
        record=(0xF00C).to_bytes(2,"little")+payload
        x=decode_known_history_record(record)
        self.assertEqual(x["decoded"]["sg_value"],123)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"x.sqlite"
            result=ingest_history_record(record,p,datetime(2026,1,1,tzinfo=timezone.utc))
            self.assertTrue(result["stored"])
            con=open_db(p)
            try:self.assertEqual(con.execute("SELECT value FROM sensor_readings").fetchone()[0],123)
            finally:con.close()

    def test_special_sg_is_not_invented(self):
        payload=(0).to_bytes(2,"little",signed=True)+(0x0303).to_bytes(2,"little")+(0).to_bytes(2,"little")+(0).to_bytes(2,"little",signed=True)
        x=decode_sg_measurement_payload(payload)
        self.assertIsNone(x["sg_value"])
        self.assertEqual(x["sg_state"],"sensor_updating")

    def test_physical_boundary_blocks_active_operations(self):
        with tempfile.TemporaryDirectory() as d:
            s=ExternalReadOnlyByteSink(Path(d)/"r.jsonl")
            s.accept_received_bytes("test",b"abc")
            with self.assertRaises(RuntimeError):s.write(b"x")
            with self.assertRaises(RuntimeError):s.pair()
            with self.assertRaises(RuntimeError):s.handshake()

if __name__=="__main__": unittest.main()
