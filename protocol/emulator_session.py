"""Integration helpers for the project-owned BLE emulator.

Persists emulator lifecycle/read events to the local SQLite database only.
No pump protocol or pump connection is present here.
"""
from protocol.session_simulator import LocalSession, record_event
from storage.db import open_db

class EmulatorSessionLog:
    def __init__(self, db_path):
        self.con = open_db(db_path)
        self.session = LocalSession()
        self.closed = False

    def start(self, service_uuid):
        record_event(self.con, "emulator_session_created", {
            "state": self.session.state.value,
            "service_uuid": str(service_uuid),
        })
        self.session.open()
        record_event(self.con, "emulator_session_opened", {
            "state": self.session.state.value,
        })

    def record_read(self, characteristic_uuid):
        record_event(self.con, "emulator_gatt_read", {
            "state": self.session.state.value,
            "characteristic_uuid": str(characteristic_uuid),
        })

    def finish(self):
        if self.closed:
            return
        if self.session.state.value == "OPEN":
            self.session.close()
            record_event(self.con, "emulator_session_closed", {
                "state": self.session.state.value,
            })
        self.closed = True

    def event_count(self):
        return self.con.execute(
            "SELECT COUNT(*) FROM pump_events WHERE source='local-session-simulator' "
            "AND event_type LIKE 'emulator_%'"
        ).fetchone()[0]

    def close_db(self):
        self.con.close()
