import unittest
from protocol.offline_timestamp import inspect_ngp_timestamp


class OfflineTimestampTests(unittest.TestCase):
    def test_explicit_confirmation_required(self):
        with self.assertRaises(ValueError):
            inspect_ngp_timestamp(0, 0)

    def test_epoch(self):
        result = inspect_ngp_timestamp(0, 0, confirm_ngp_format=True)
        self.assertEqual(result["timestamp_utc"], "2000-01-01T00:00:00+00:00")
        self.assertFalse(result["validated_for_780g"])

    def test_offset_seconds(self):
        result = inspect_ngp_timestamp(60, -30, confirm_ngp_format=True)
        self.assertEqual(result["timestamp_utc"], "2000-01-01T00:00:30+00:00")

    def test_reject_invalid_types(self):
        for rtc, offset in [(True, 0), (-1, 0), (2**32, 0), (1.5, 0), (0, True), (0, 2**31)]:
            with self.subTest(rtc=rtc, offset=offset):
                with self.assertRaises(ValueError):
                    inspect_ngp_timestamp(rtc, offset, confirm_ngp_format=True)


if __name__ == "__main__":
    unittest.main()
