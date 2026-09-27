"""Local Windows GATT test service.

Uses project-owned UUIDs and does not implement, imitate, scan for, or connect
to any insulin-pump protocol. It exists only to validate Windows peripheral
role support.
"""
import asyncio
from uuid import UUID

TEST_SERVICE_UUID = UUID("a46b7b20-9b67-4ad6-9d18-4b694c0bde01")

async def run_test_service(seconds: int = 15) -> dict:
    if seconds < 1 or seconds > 120:
        raise ValueError("seconds must be between 1 and 120")

    from winrt.windows.devices.bluetooth.genericattributeprofile import (
        GattServiceProvider,
        GattServiceProviderAdvertisingParameters,
    )

    result = await GattServiceProvider.create_async(TEST_SERVICE_UUID)
    error = str(result.error)
    provider = result.service_provider
    if provider is None:
        return {"started": False, "error": error, "service_uuid": str(TEST_SERVICE_UUID)}

    params = GattServiceProviderAdvertisingParameters()
    params.is_connectable = True
    params.is_discoverable = True

    provider.start_advertising(params)
    try:
        # Keep a strong reference to provider while Windows advertises.
        await asyncio.sleep(seconds)
        return {
            "started": True,
            "service_uuid": str(TEST_SERVICE_UUID),
            "seconds": seconds,
            "advertisement_status": str(provider.advertisement_status),
            "protocol_enabled": False,
            "safe_mode": "test-service-only",
        }
    finally:
        provider.stop_advertising()

def run(seconds: int = 15) -> dict:
    return asyncio.run(run_test_service(seconds))
