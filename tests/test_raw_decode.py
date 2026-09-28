import tempfile
import unittest
from pathlib import Path
from protocol.raw_capture import RawPacketRecorder,replay
from protocol.cgm_decoder import decode_cgm_measurement

class RawDecodeTests(unittest.TestCase):
    def test_capture_replay(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"raw.jsonl"; RawPacketRecorder(p).record("x",b"\\x01\\x02")
            rows=list(replay(p)); self.assertEqual(rows[0]["data"],b"\\x01\\x02")

    def test_minimal_cgm_record(self):
        # size=6, flags=0, SFLOAT mantissa=123 exponent=0, offset=5
        raw=bytes([6,0,0x7B,0x00,5,0])
        x=decode_cgm_measurement(raw)
        self.assertEqual(x["glucose"],123.0)
        self.assertEqual(x["time_offset_minutes"],5)

    def test_bad_size_rejected(self):
        with self.assertRaises(ValueError): decode_cgm_measurement(bytes([7,0,0x7B,0,0,0]))

if __name__=="__main__": unittest.main()
