import json
from pathlib import Path
from protocol.readonly_gate import Operation, authorize
from .base import PumpTransport

class SimulatorTransport(PumpTransport):
    def __init__(self, fixture_path=None):
        self.connected = False
        self.fixture_path = Path(fixture_path) if fixture_path else None
        self.fixtures = {}
        if self.fixture_path and self.fixture_path.exists():
            self.fixtures = json.loads(self.fixture_path.read_text(encoding="utf-8"))

    def connect(self): self.connected = True
    def disconnect(self): self.connected = False

    def execute(self, operation: Operation) -> bytes:
        if not self.connected:
            raise RuntimeError("Simulator is not connected")
        authorize(operation)
        value = self.fixtures.get(operation.name, {"ok": True, "operation": operation.name})
        return json.dumps(value, ensure_ascii=False).encode("utf-8")
