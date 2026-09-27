"""Windows BLE capability diagnostics.

No MiniMed protocol commands are implemented here. This module only checks
whether the Windows Python/WinRT environment exposes BLE building blocks.
"""
import importlib
import platform

COMPONENTS = {
    "advertisement_publisher": (
        "winrt.windows.devices.bluetooth.advertisement",
        "BluetoothLEAdvertisementPublisher",
    ),
    "gatt_service_provider": (
        "winrt.windows.devices.bluetooth.genericattributeprofile",
        "GattServiceProvider",
    ),
    "remote_ble_device": (
        "winrt.windows.devices.bluetooth",
        "BluetoothLEDevice",
    ),
}

class WindowsWinRTTransport:
    def _component_probe(self, module_name, symbol):
        try:
            module = importlib.import_module(module_name)
            return {"available": hasattr(module, symbol), "module": module_name, "symbol": symbol}
        except Exception as exc:
            return {"available": False, "module": module_name, "symbol": symbol,
                    "error": f"{type(exc).__name__}: {exc}"}

    def probe(self) -> dict:
        result = {
            "platform": platform.platform(),
            "windows": platform.system() == "Windows",
            "winrt_importable": False,
            "components": {},
            "ble_stack_ready": False,
            "protocol_enabled": False,
            "safe_mode": "diagnostics-only",
        }
        if not result["windows"]:
            result["reason"] = "Run this probe on Windows 10/11."
            return result
        try:
            importlib.import_module("winrt")
            result["winrt_importable"] = True
        except Exception as exc:
            result["reason"] = f"WinRT Python package unavailable: {type(exc).__name__}: {exc}"
            return result

        for name, (module_name, symbol) in COMPONENTS.items():
            result["components"][name] = self._component_probe(module_name, symbol)

        result["ble_stack_ready"] = all(
            item["available"] for item in result["components"].values()
        )
        if not result["ble_stack_ready"]:
            result["reason"] = (
                "One or more Windows BLE WinRT components are unavailable. "
                "No BLE session was started."
            )
        else:
            result["next_step"] = (
                "WinRT BLE primitives are present. Next test should use only a "
                "local simulator/test peripheral before any pump protocol is enabled."
            )
        return result
