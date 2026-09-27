"""Windows BLE scanner for the project-owned GATT test UUID only.

It does not search for MiniMed devices and does not contain pump protocol code.
"""
import asyncio
from uuid import UUID

TEST_SERVICE_UUID = UUID("a46b7b20-9b67-4ad6-9d18-4b694c0bde01")

async def scan(seconds: int = 10) -> dict:
    if seconds < 1 or seconds > 120:
        raise ValueError("seconds must be between 1 and 120")

    from winrt.windows.devices.bluetooth.advertisement import (
        BluetoothLEAdvertisementWatcher,
    )

    watcher = BluetoothLEAdvertisementWatcher()
    found = []
    seen = set()

    def received(sender, args):
        try:
            uuids = [str(x).lower() for x in args.advertisement.service_uuids]
            if str(TEST_SERVICE_UUID).lower() in uuids:
                address = int(args.bluetooth_address)
                if address not in seen:
                    seen.add(address)
                    found.append({
                        "bluetooth_address": f"{address:012X}",
                        "rssi": int(args.raw_signal_strength_in_dbm),
                    })
        except Exception:
            pass

    token = watcher.add_received(received)
    watcher.start()
    try:
        await asyncio.sleep(seconds)
    finally:
        watcher.stop()
        try:
            watcher.remove_received(token)
        except Exception:
            pass

    return {
        "scan_seconds": seconds,
        "service_uuid": str(TEST_SERVICE_UUID),
        "matches": found,
        "match_count": len(found),
        "protocol_enabled": False,
        "safe_mode": "test-uuid-scan-only",
        "note": (
            "Zero matches on the same PC is not a failure: many Bluetooth adapters/"
            "drivers do not report their own local advertisement back to themselves."
        ),
    }

def run(seconds: int = 10) -> dict:
    return asyncio.run(scan(seconds))
