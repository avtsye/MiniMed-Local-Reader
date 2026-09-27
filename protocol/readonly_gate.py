from dataclasses import dataclass

class UnsafeOperationError(RuntimeError):
    pass

@dataclass(frozen=True)
class Operation:
    name: str
    payload: bytes = b""

# Deliberately semantic only: no pump opcodes are embedded until independently verified.
ALLOWED_OPERATIONS = frozenset({
    "session_handshake",
    "read_device_info",
    "read_status",
    "read_cgm",
    "read_history",
})

THERAPY_KEYWORDS = ("bolus", "basal_set", "deliver", "suspend", "resume", "target_set", "therapy_set")

def authorize(operation: Operation) -> None:
    lower = operation.name.lower()
    if any(word in lower for word in THERAPY_KEYWORDS):
        raise UnsafeOperationError(f"Therapy-changing operation blocked: {operation.name}")
    if operation.name not in ALLOWED_OPERATIONS:
        raise UnsafeOperationError(f"Unknown/unverified operation blocked: {operation.name}")
