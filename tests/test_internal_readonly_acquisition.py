import tempfile
import unittest
from pathlib import Path

from datasource.internal_readonly import InternalReadOnlyAcquisition
from storage.db import open_db

class InternalReadOnlyAcquisitionTests(unittest.TestCase):
    def test_raw_packet_is_captured_without_command_capabilities(self):
        with tempfile.TemporaryDirectory() as d:
            db = Path(d) / "reader.sqlite"
            capture = Path(d) / "capture.jsonl"
            source = InternalReadOnlyAcquisition(db, capture)
            result = source.accept_received("raw", b"\x01\x02\x03", {"test": True})
            self.assertTrue(result["accepted"])
            self.assertEqual(result["byte_count"], 3)
            self.assertFalse(result["writes_enabled"])
            self.assertFalse(result["commands_enabled"])
            self.assertFalse(result["pairing_enabled"])
            self.assertEqual(capture.read_text(encoding="utf-8").count("\n"), 1)

    def test_unknown_channel_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            source = InternalReadOnlyAcquisition(Path(d) / "reader.sqlite")
            with self.assertRaises(ValueError):
                source.accept_received("device_command", b"\x01")

    def test_capabilities_are_receive_only(self):
        with tempfile.TemporaryDirectory() as d:
            source = InternalReadOnlyAcquisition(Path(d) / "reader.sqlite")
            caps = source.capabilities
            self.assertTrue(caps["receive_bytes"])
            self.assertFalse(caps["writes"])
            self.assertFalse(caps["commands"])
            self.assertFalse(caps["pairing"])
            self.assertFalse(caps["therapy_operations"])

if __name__ == "__main__":
    unittest.main()
