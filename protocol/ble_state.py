"""Safety-first BLE connection lifecycle.

Infrastructure only: no device-specific protocol, pairing, GATT writes, or
therapy operations.
"""
from dataclasses import dataclass
from enum import Enum

class BleState(str, Enum):
    IDLE="IDLE"
    DISCOVERING="DISCOVERING"
    CANDIDATE_FOUND="CANDIDATE_FOUND"
    CONNECTING="CONNECTING"
    CONNECTED_READ_ONLY="CONNECTED_READ_ONLY"
    DISCONNECTED="DISCONNECTED"
    FAILED="FAILED"

@dataclass
class BleSessionState:
    state: BleState = BleState.IDLE
    candidate_address: str | None = None
    error: str | None = None

    def transition(self, new_state, address=None, error=None):
        allowed={
            BleState.IDLE:{BleState.DISCOVERING},
            BleState.DISCOVERING:{BleState.CANDIDATE_FOUND,BleState.FAILED,BleState.DISCONNECTED},
            BleState.CANDIDATE_FOUND:{BleState.CONNECTING,BleState.DISCONNECTED,BleState.FAILED},
            BleState.CONNECTING:{BleState.CONNECTED_READ_ONLY,BleState.FAILED,BleState.DISCONNECTED},
            BleState.CONNECTED_READ_ONLY:{BleState.DISCONNECTED,BleState.FAILED},
            BleState.DISCONNECTED:{BleState.DISCOVERING},
            BleState.FAILED:{BleState.DISCOVERING,BleState.DISCONNECTED},
        }
        if new_state not in allowed[self.state]:
            raise RuntimeError(f"Invalid BLE transition: {self.state.value} -> {new_state.value}")
        self.state=new_state
        if address is not None:self.candidate_address=address
        self.error=error
        return self.state
