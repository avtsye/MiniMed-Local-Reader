import unittest
from protocol.readonly_gate import Operation, authorize, UnsafeOperationError

class GateTests(unittest.TestCase):
    def test_read_allowed(self):
        authorize(Operation("read_history"))
    def test_unknown_blocked(self):
        with self.assertRaises(UnsafeOperationError): authorize(Operation("mystery_command"))
    def test_therapy_blocked(self):
        with self.assertRaises(UnsafeOperationError): authorize(Operation("deliver_bolus"))

if __name__ == "__main__": unittest.main()
