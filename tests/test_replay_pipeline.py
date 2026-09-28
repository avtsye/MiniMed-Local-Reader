import tempfile
import unittest
from pathlib import Path
from protocol.framing import frame,LengthPrefixedReassembler
from protocol.history_decoder import decode_history_envelope
from protocol.raw_capture import RawPacketRecorder
from protocol.replay_pipeline import decode_replay

class ReplayPipelineTests(unittest.TestCase):
    def test_fragment_reassembly(self):
        raw=frame(b"hello"); a=LengthPrefixedReassembler()
        self.assertEqual(a.feed(raw[:3]),[])
        self.assertEqual(a.feed(raw[3:]),[b"hello"])

    def test_history_catalog(self):
        x=decode_history_envelope(bytes.fromhex("0CF0AABB"))
        self.assertEqual(x["event_name"],"SG_MEASUREMENT")
        self.assertEqual(x["payload_hex"],"AABB")

    def test_mixed_replay(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"r.jsonl"; rec=RawPacketRecorder(p)
            rec.record("cgm_measurement",bytes([6,0,0x7B,0,0,0]))
            rec.record("history_record",bytes.fromhex("0CF0AABB"))
            result=decode_replay(p)
            self.assertEqual(result[0]["decoded"]["glucose"],123.0)
            self.assertEqual(result[1]["decoded"]["event_name"],"SG_MEASUREMENT")

if __name__=="__main__": unittest.main()
