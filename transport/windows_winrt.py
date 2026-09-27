"""Windows BLE compatibility probe.

This module intentionally does NOT contain MiniMed protocol commands.
Its first milestone is adapter/GATT capability detection only.
"""
import platform

class WindowsWinRTTransport:
    def probe(self) -> dict:
        result = {
            "platform": platform.platform(),
            "windows": platform.system() == "Windows",
            "winrt_importable": False,
            "protocol_enabled": False,
        }
        if not result["windows"]:
            result["reason"] = "Run this probe on Windows 10/11."
            return result
        try:
            import winrt  # noqa: F401
            result["winrt_importable"] = True
        except Exception as exc:
            result["reason"] = f"WinRT Python package unavailable: {exc}"
        return result
