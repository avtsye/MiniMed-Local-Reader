from abc import ABC, abstractmethod
from protocol.readonly_gate import Operation

class PumpTransport(ABC):
    @abstractmethod
    def connect(self) -> None: ...
    @abstractmethod
    def disconnect(self) -> None: ...
    @abstractmethod
    def execute(self, operation: Operation) -> bytes: ...
