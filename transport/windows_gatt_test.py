"""Local Windows GATT test service.

Project-owned UUID only. No MiniMed protocol is implemented or enabled.
"""
import asyncio
from uuid import UUID

TEST_SERVICE_UUID = UUID("a46b7b20-9b67-4ad6-9d18-4b694c0bde01")

async def run_test_service(seconds: int = 15) -> dict:
    if seconds < 1 or seconds > 120:
        raise ValueError("seconds must be between 1 and 120")

    from winrt.windows.devices.bluetooth.genericattributeprofile import GattServiceProvider

    result = await GattServiceProvider.create_async(TEST_SERVICE_UUID)
    provider = result.service_provider
    base = {
        "service_uuid": str(TEST_SERVICE_UUID),
        "create_error": str(result.error),
        "protocol_enabled": False,
        "safe_mode": "test-service-only",
    }
    if provider is None:
        return {**base, "started": False, "reason": "GattServiceProvider.create_async returned no provider"}

    # Python WinRT projections differ: some expose only start_advertising(),
    # while others expose an overload accepting advertising parameters.
    start_variant = None
    try:
        provider.start_advertising()
        start_variant = "no-arguments"
    except TypeError as no_arg_error:
        try:
            from winrt.windows.devices.bluetooth.genericattributeprofile import (
                GattServiceProviderAdvertisingParameters,
            )
            params = GattServiceProviderAdvertisingParameters()
            params.is_connectable = True
            params.is_discoverable = True
            provider.start_advertising(params)
            start_variant = "advertising-parameters"
        except Exception as param_error:
            return {
                **base,
                "started": False,
                "reason": "No supported start_advertising overload succeeded",
                "no_argument_error": f"{type(no_arg_error).__name__}: {no_arg_error}",
                "parameter_error": f"{type(param_error).__name__}: {param_error}",
            }
    except Exception as exc:
        return {**base, "started": False, "reason": f"{type(exc).__name__}: {exc}"}

    try:
        await asyncio.sleep(seconds)
        return {
            **base,
            "started": True,
            "seconds": seconds,
            "start_variant": start_variant,
            "advertisement_status": str(provider.advertisement_status),
        }
    finally:
        try:
            provider.stop_advertising()
        except Exception:
            pass

def run(seconds: int = 15) -> dict:
    try:
        return asyncio.run(run_test_service(seconds))
    except Exception as exc:
        return {
            "started": False,
            "protocol_enabled": False,
            "safe_mode": "test-service-only",
            "reason": f"Unhandled diagnostic error: {type(exc).__name__}: {exc}",
        }
