"""Offline timestamp inspection helpers; no device access.

The 2000-01-01 epoch is an NGP research hypothesis from static analysis,
NOT a verified MiniMed 700/780G timestamp specification.
"""
from datetime import datetime, timedelta, timezone

NGP_EPOCH_UNIX_SECONDS = 946684800
MIN_RTC = 0
MAX_RTC = 0xFFFFFFFF


def inspect_ngp_timestamp(rtc, offset_seconds, *, confirm_ngp_format=False):
    """Inspect a pre-exported timestamp, never infer its device format.

    Offset is interpreted as seconds only when caller explicitly confirms
    the NGP interpretation. Returned timestamps are timezone-aware UTC.
    """
    if not confirm_ngp_format:
        raise ValueError("NGP timestamp interpretation requires explicit confirmation")
    if isinstance(rtc, bool) or not isinstance(rtc, int) or not MIN_RTC <= rtc <= MAX_RTC:
        raise ValueError("rtc must be an unsigned 32-bit integer")
    if isinstance(offset_seconds, bool) or not isinstance(offset_seconds, int):
        raise ValueError("offset_seconds must be an integer")
    if not -(2**31) <= offset_seconds < 2**31:
        raise ValueError("offset_seconds outside signed 32-bit range")
    unix_seconds = NGP_EPOCH_UNIX_SECONDS + rtc + offset_seconds
    try:
        result = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=unix_seconds)
    except (OverflowError, ValueError) as exc:
        raise ValueError("timestamp outside supported datetime range") from exc
    return {
        "timestamp_utc": result.isoformat(),
        "rtc": rtc,
        "offset_seconds": offset_seconds,
        "assumption": "NGP-only; 2000-01-01 UTC epoch and seconds offset",
        "validated_for_780g": False,
    }
