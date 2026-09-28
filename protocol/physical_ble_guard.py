"""Hard safety boundary for future physical BLE work."""

class BleWriteBlocked(RuntimeError):
    pass

class PairingBlocked(RuntimeError):
    pass

def block_write(*_args, **_kwargs):
    raise BleWriteBlocked("BLE writes are disabled by project safety policy")

def block_pairing(*_args, **_kwargs):
    raise PairingBlocked("Pairing is disabled in the current physical-BLE stage")

def safety_status():
    return {
        "physical_ble_stage": "infrastructure-only",
        "protocol_enabled": False,
        "pairing_enabled": False,
        "gatt_writes_enabled": False,
        "therapy_operations_enabled": False,
        "safe_mode": "physical-ble-readonly-infrastructure",
    }
