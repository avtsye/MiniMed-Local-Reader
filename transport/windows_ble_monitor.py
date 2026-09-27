"""Passive live BLE signal monitor.

No connections, pairing, GATT access, writes, or pump protocol.
"""
import asyncio
import time

async def monitor(seconds: int = 30) -> dict:
    if seconds < 5 or seconds > 300:
        raise ValueError("seconds must be between 5 and 300")

    from winrt.windows.devices.bluetooth.advertisement import (
        BluetoothLEAdvertisementWatcher,
        BluetoothLEScanningMode,
    )

    watcher = BluetoothLEAdvertisementWatcher()
    watcher.scanning_mode = BluetoothLEScanningMode.ACTIVE
    devices = {}

    def received(sender, args):
        try:
            address = f"{int(args.bluetooth_address):012X}"
            adv = args.advertisement
            row = devices.setdefault(address, {
                "bluetooth_address": address,
                "address_type": str(args.bluetooth_address_type),
                "local_name": "",
                "service_uuids": [],
                "samples": 0,
                "rssi_min": 127,
                "rssi_max": -127,
                "rssi_sum": 0,
                "last_seen": 0.0,
            })
            rssi = int(args.raw_signal_strength_in_dbm)
            row["samples"] += 1
            row["rssi_min"] = min(row["rssi_min"], rssi)
            row["rssi_max"] = max(row["rssi_max"], rssi)
            row["rssi_sum"] += rssi
            row["last_seen"] = time.time()
            if adv.local_name:
                row["local_name"] = str(adv.local_name)
            uuids = {str(x) for x in adv.service_uuids}
            if uuids:
                row["service_uuids"] = sorted(set(row["service_uuids"]) | uuids)
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

    rows = []
    for row in devices.values():
        samples = row.pop("samples")
        total = row.pop("rssi_sum")
        row["samples"] = samples
        row["rssi_avg"] = round(total / samples, 1) if samples else None
        row.pop("last_seen", None)
        rows.append(row)

    rows.sort(key=lambda x: (x["samples"], x["rssi_avg"] or -999), reverse=True)
    return {
        "monitor_seconds": seconds,
        "device_count": len(rows),
        "devices": rows,
        "connected": False,
        "pairing_started": False,
        "writes_enabled": False,
        "protocol_enabled": False,
        "safe_mode": "passive-live-monitor-only",
    }

def run(seconds: int = 30) -> dict:
    try:
        return asyncio.run(monitor(seconds))
    except Exception as exc:
        return {
            "device_count": 0,
            "devices": [],
            "connected": False,
            "pairing_started": False,
            "writes_enabled": False,
            "protocol_enabled": False,
            "safe_mode": "passive-live-monitor-only",
            "reason": f"{type(exc).__name__}: {exc}",
        }
