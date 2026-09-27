"""Passive Windows BLE discovery diagnostics.

Listens to advertisements only. No connection, pairing, GATT access, writes,
or pump protocol are performed.
"""
import asyncio

def _hex_buffer(buffer):
    try:
        from winrt.windows.storage.streams import DataReader
        reader = DataReader.from_buffer(buffer)
        data = bytearray(reader.unconsumed_buffer_length)
        reader.read_bytes(data)
        return data.hex().upper()
    except Exception:
        return ""

async def discover(seconds: int = 10, max_devices: int = 50) -> dict:
    if seconds < 1 or seconds > 120:
        raise ValueError("seconds must be between 1 and 120")
    if max_devices < 1 or max_devices > 500:
        raise ValueError("max_devices must be between 1 and 500")

    from winrt.windows.devices.bluetooth.advertisement import (
        BluetoothLEAdvertisementWatcher,
        BluetoothLEScanningMode,
    )

    watcher = BluetoothLEAdvertisementWatcher()
    watcher.scanning_mode = BluetoothLEScanningMode.ACTIVE
    devices = {}

    def received(sender, args):
        try:
            address = int(args.bluetooth_address)
            key = f"{address:012X}"
            advertisement = args.advertisement
            manufacturers = []
            for item in advertisement.manufacturer_data:
                manufacturers.append({
                    "company_id": int(item.company_id),
                    "data_hex": _hex_buffer(item.data),
                })
            sections = []
            for section in advertisement.data_sections:
                sections.append({
                    "data_type": int(section.data_type),
                    "data_hex": _hex_buffer(section.data),
                })

            item = {
                "bluetooth_address": key,
                "bluetooth_address_type": str(args.bluetooth_address_type),
                "rssi": int(args.raw_signal_strength_in_dbm),
                "local_name": str(advertisement.local_name or ""),
                "service_uuids": sorted({str(x) for x in advertisement.service_uuids}),
                "manufacturer_data": manufacturers,
                "data_sections": sections,
            }
            current = devices.get(key)
            if current is None or len(str(item)) > len(str(current)):
                devices[key] = item
            else:
                current["rssi"] = item["rssi"]

            if len(devices) > max_devices:
                weakest = min(devices, key=lambda k: devices[k]["rssi"])
                devices.pop(weakest, None)
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

    ordered = sorted(devices.values(), key=lambda x: x["rssi"], reverse=True)
    return {
        "scan_seconds": seconds,
        "device_count": len(ordered),
        "devices": ordered,
        "connected": False,
        "writes_enabled": False,
        "protocol_enabled": False,
        "safe_mode": "passive-advertisement-discovery-only",
    }

def run(seconds: int = 10, max_devices: int = 50) -> dict:
    try:
        return asyncio.run(discover(seconds, max_devices))
    except Exception as exc:
        return {
            "device_count": 0,
            "devices": [],
            "connected": False,
            "writes_enabled": False,
            "protocol_enabled": False,
            "safe_mode": "passive-advertisement-discovery-only",
            "reason": f"{type(exc).__name__}: {exc}",
        }
