import unittest
from transport.windows_mobile_emulator import SERVICE_UUID, INFO_UUID, STATE_UUID, VALUES

class EmulatorClientContractTests(unittest.TestCase):
    def test_project_owned_contract(self):
        self.assertNotEqual(SERVICE_UUID, INFO_UUID)
        self.assertNotEqual(SERVICE_UUID, STATE_UUID)
        self.assertEqual(VALUES[INFO_UUID], b"MiniMedLocalReader-MobileEmulator")
        self.assertEqual(VALUES[STATE_UUID], b"READY_READ_ONLY")

if __name__ == "__main__":
    unittest.main()
