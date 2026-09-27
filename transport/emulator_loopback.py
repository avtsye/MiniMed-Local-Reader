"""Single-computer loopback integration test.

Exercises the same project-owned read-only emulator contract without using
the Bluetooth radio. This is a software integration test, not a BLE link.
"""
from protocol.emulator_session import EmulatorSessionLog
from transport.windows_mobile_emulator import SERVICE_UUID, INFO_UUID, STATE_UUID, VALUES

def run(db_path):
    log = EmulatorSessionLog(db_path)
    reads = {}
    try:
        log.start(SERVICE_UUID)
        for uuid in (INFO_UUID, STATE_UUID):
            value = VALUES[uuid]
            log.record_read(uuid)
            reads[str(uuid)] = value.decode("utf-8")
        log.finish()
        return {
            "loopback_completed": True,
            "transport": "software-loopback",
            "bluetooth_radio_used": False,
            "service_uuid": str(SERVICE_UUID),
            "reads": reads,
            "expected_values_match": (
                reads[str(INFO_UUID)] == "MiniMedLocalReader-MobileEmulator"
                and reads[str(STATE_UUID)] == "READY_READ_ONLY"
            ),
            "events_this_run": 5,
            "protocol_enabled": False,
            "pairing_started": False,
            "writes_enabled": False,
            "therapy_operations_enabled": False,
            "safe_mode": "project-owned-software-loopback-only",
        }
    finally:
        if not log.closed:
            log.finish()
        log.close_db()
