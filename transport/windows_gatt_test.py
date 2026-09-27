"""Local Windows GATT test service.

Project-owned UUIDs only. No MiniMed protocol is implemented or enabled.
"""
import asyncio
from uuid import UUID

TEST_SERVICE_UUID = UUID("a46b7b20-9b67-4ad6-9d18-4b694c0bde01")
TEST_CHARACTERISTIC_UUID = UUID("a46b7b20-9b67-4ad6-9d18-4b694c0bde02")

async def run_test_service(seconds: int = 15) -> dict:
    if seconds < 1 or seconds > 120:
        raise ValueError("seconds must be between 1 and 120")

    from winrt.windows.devices.bluetooth.genericattributeprofile import (
        GattCharacteristicProperties,
        GattLocalCharacteristicParameters,
        GattProtectionLevel,
        GattServiceProvider,
    )

    result = await GattServiceProvider.create_async(TEST_SERVICE_UUID)
    provider = result.service_provider
    base = {
        "service_uuid": str(TEST_SERVICE_UUID),
        "characteristic_uuid": str(TEST_CHARACTERISTIC_UUID),
        "create_error": str(result.error),
        "protocol_enabled": False,
        "safe_mode": "test-service-only",
    }
    if provider is None:
        return {**base, "started": False, "reason": "GattServiceProvider.create_async returned no provider"}

    characteristic = None
    try:
        params = GattLocalCharacteristicParameters()
        # Deliberately read-only: the test characteristic accepts no writes.
        params.characteristic_properties = GattCharacteristicProperties.READ
        params.read_protection_level = GattProtectionLevel.PLAIN
        char_result = await provider.service.create_characteristic_async(
            TEST_CHARACTERISTIC_UUID, params
        )
        characteristic = char_result.characteristic
        base["characteristic_error"] = str(char_result.error)
        base["characteristic_created"] = characteristic is not None
    except Exception as exc:
        return {
            **base,
            "started": False,
            "characteristic_created": False,
            "reason": f"Characteristic creation failed: {type(exc).__name__}: {exc}",
        }

    if characteristic is None:
        return {**base, "started": False, "reason": "No local characteristic was created"}

    read_count = 0
    read_event = asyncio.Event()

    def on_read_requested(sender, args):
        nonlocal read_count
        async def respond():
            nonlocal read_count
            try:
                request = await args.get_request_async()
                if request is None:
                    return
                from winrt.windows.storage.streams import DataWriter
                writer = DataWriter()
                writer.write_bytes(TEST_VALUE)
                request.respond_with_value(writer.detach_buffer())
                read_count += 1
                read_event.set()
            except Exception:
                # Test harness only: keep advertising even if one client read fails.
                pass
        asyncio.create_task(respond())

    characteristic.add_read_requested(on_read_requested)

    start_variant = None
    try:
        provider.start_advertising()
        start_variant = "no-arguments"
    except TypeError as no_arg_error:
        try:
            from winrt.windows.devices.bluetooth.genericattributeprofile import (
                GattServiceProviderAdvertisingParameters,
            )
            adv = GattServiceProviderAdvertisingParameters()
            adv.is_connectable = True
            adv.is_discoverable = True
            provider.start_advertising(adv)
            start_variant = "advertising-parameters"
        except Exception as param_error:
            return {
                **base, "started": False,
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
            "characteristic_mode": "read-only",
            "read_requests": read_count,
            "test_value": TEST_VALUE.decode("ascii"),
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
