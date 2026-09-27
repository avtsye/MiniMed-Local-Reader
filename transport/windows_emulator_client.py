"""Read-only client for the project-owned local BLE emulator.

This module is intentionally restricted to the emulator UUIDs. It performs
no pairing and exposes no write operation.
"""
import asyncio
from uuid import UUID

from transport.windows_mobile_emulator import SERVICE_UUID, INFO_UUID, STATE_UUID

def _buffer_bytes(buffer):
    from winrt.windows.storage.streams import DataReader
    reader = DataReader.from_buffer(buffer)
    data = bytearray(reader.unconsumed_buffer_length)
    reader.read_bytes(data)
    return bytes(data)

async def read_emulator(address: int):
    from winrt.windows.devices.bluetooth import BluetoothLEDevice
    from winrt.windows.devices.bluetooth.genericattributeprofile import BluetoothCacheMode

    device = await BluetoothLEDevice.from_bluetooth_address_async(address)
    if device is None:
        raise RuntimeError("Could not open the local emulator device")

    try:
        services_result = await device.get_gatt_services_for_uuid_async(
            SERVICE_UUID, BluetoothCacheMode.UNCACHED
        )
        if not services_result.services:
            raise RuntimeError("Project-owned emulator service was not found")
        service = services_result.services[0]

        values = {}
        for uuid in (INFO_UUID, STATE_UUID):
            chars = await service.get_characteristics_for_uuid_async(
                uuid, BluetoothCacheMode.UNCACHED
            )
            if not chars.characteristics:
                raise RuntimeError(f"Emulator characteristic not found: {uuid}")
            result = await chars.characteristics[0].read_value_async(BluetoothCacheMode.UNCACHED)
            raw = _buffer_bytes(result.value)
            values[str(uuid)] = raw.decode("utf-8", errors="replace")

        return {
            "connected_to_project_emulator": True,
            "service_uuid": str(SERVICE_UUID),
            "values": values,
            "expected_values_match": (
                values[str(INFO_UUID)] == "MiniMedLocalReader-MobileEmulator"
                and values[str(STATE_UUID)] == "READY_READ_ONLY"
            ),
            "pairing_started": False,
            "writes_enabled": False,
            "protocol_enabled": False,
            "safe_mode": "project-owned-emulator-client-only",
        }
    finally:
        device.close()

async def discover_and_read(seconds=15):
    from winrt.windows.devices.bluetooth.advertisement import (
        BluetoothLEAdvertisementWatcher,
        BluetoothLEScanningMode,
    )

    found = asyncio.get_running_loop().create_future()
    watcher = BluetoothLEAdvertisementWatcher()
    watcher.scanning_mode = BluetoothLEScanningMode.ACTIVE

    def received(sender, args):
        try:
            advertised = {str(x).lower() for x in args.advertisement.service_uuids}
            if str(SERVICE_UUID).lower() in advertised and not found.done():
                found.set_result(int(args.bluetooth_address))
        except Exception:
            pass

    token = watcher.add_received(received)
    watcher.start()
    try:
        address = await asyncio.wait_for(found, timeout=seconds)
    finally:
        watcher.stop()
        try:
            watcher.remove_received(token)
        except Exception:
            pass
    return await read_emulator(address)

def run(seconds=15):
    try:
        return asyncio.run(discover_and_read(seconds))
    except Exception as exc:
        return {
            "connected_to_project_emulator": False,
            "pairing_started": False,
            "writes_enabled": False,
            "protocol_enabled": False,
            "safe_mode": "project-owned-emulator-client-only",
            "reason": f"{type(exc).__name__}: {exc}",
        }
