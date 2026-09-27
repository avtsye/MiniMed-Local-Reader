"""Local Mobile-side BLE architecture emulator.

Uses project-owned UUIDs only. It does not implement MiniMed pairing, SAKE,
pump commands, or therapy operations. The exposed characteristics are
read-only diagnostics for validating the Windows GATT-server architecture.
"""
import asyncio
from uuid import UUID

SERVICE_UUID = UUID("a46b7b20-9b67-4ad6-9d18-4b694c0bdf01")
INFO_UUID = UUID("a46b7b20-9b67-4ad6-9d18-4b694c0bdf02")
STATE_UUID = UUID("a46b7b20-9b67-4ad6-9d18-4b694c0bdf03")

VALUES = {
    INFO_UUID: b"MiniMedLocalReader-MobileEmulator",
    STATE_UUID: b"READY_READ_ONLY",
}

async def _create_readonly_characteristic(service, uuid, value, counters, session_log=None):
    from winrt.windows.devices.bluetooth.genericattributeprofile import (
        GattCharacteristicProperties,
        GattLocalCharacteristicParameters,
        GattProtectionLevel,
    )
    params = GattLocalCharacteristicParameters()
    params.characteristic_properties = GattCharacteristicProperties.READ
    params.read_protection_level = GattProtectionLevel.PLAIN
    result = await service.create_characteristic_async(uuid, params)
    characteristic = result.characteristic
    if characteristic is None:
        raise RuntimeError(f"Could not create characteristic {uuid}: {result.error}")

    def on_read_requested(sender, args):
        async def respond():
            try:
                request = await args.get_request_async()
                if request is None:
                    return
                from winrt.windows.storage.streams import DataWriter
                writer = DataWriter()
                writer.write_bytes(value)
                request.respond_with_value(writer.detach_buffer())
                counters[str(uuid)] += 1
                if session_log is not None:
                    session_log.record_read(uuid)
            except Exception:
                pass
        asyncio.create_task(respond())

    characteristic.add_read_requested(on_read_requested)
    return characteristic

async def run_emulator(seconds=30, db_path=None):
    if seconds < 1 or seconds > 300:
        raise ValueError("seconds must be between 1 and 300")

    from winrt.windows.devices.bluetooth.genericattributeprofile import GattServiceProvider

    created = await GattServiceProvider.create_async(SERVICE_UUID)
    provider = created.service_provider
    base = {
        "service_uuid": str(SERVICE_UUID),
        "protocol_enabled": False,
        "pairing_enabled": False,
        "writes_enabled": False,
        "therapy_operations_enabled": False,
        "safe_mode": "project-owned-mobile-emulator-only",
    }
    if provider is None:
        return {**base, "started": False, "reason": f"Service creation failed: {created.error}"}

    counters = {str(INFO_UUID): 0, str(STATE_UUID): 0}
    keepalive = []
    try:
        keepalive.append(await _create_readonly_characteristic(provider.service, INFO_UUID, VALUES[INFO_UUID], counters, session_log))
        keepalive.append(await _create_readonly_characteristic(provider.service, STATE_UUID, VALUES[STATE_UUID], counters, session_log))
        provider.start_advertising()
        await asyncio.sleep(seconds)
        return {
            **base,
            "started": True,
            "seconds": seconds,
            "advertisement_status": str(provider.advertisement_status),
            "db_events": session_log.event_count() if session_log is not None else 0,
            "characteristics": [
                {"uuid": str(INFO_UUID), "mode": "read-only", "reads": counters[str(INFO_UUID)]},
                {"uuid": str(STATE_UUID), "mode": "read-only", "reads": counters[str(STATE_UUID)]},
            ],
        }
    finally:
        try:
            provider.stop_advertising()
        except Exception:
            pass
        if session_log is not None:
            session_log.finish()
            session_log.close_db()

def run(seconds=30, db_path=None):
    try:
        return asyncio.run(run_emulator(seconds, db_path))
    except Exception as exc:
        return {
            "started": False,
            "protocol_enabled": False,
            "pairing_enabled": False,
            "writes_enabled": False,
            "therapy_operations_enabled": False,
            "safe_mode": "project-owned-mobile-emulator-only",
            "reason": f"{type(exc).__name__}: {exc}",
        }
