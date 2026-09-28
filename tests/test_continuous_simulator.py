import tempfile
import unittest
from pathlib import Path
from simulator.continuous import run
from storage.db import open_db

class ContinuousSimulatorTests(unittest.TestCase):
    def test_stress_mode_persists_synthetic_samples(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"stress.sqlite"
            result=run(path, stress_count=100)
            self.assertTrue(result["simulation_completed"])
            self.assertEqual(result["generated_samples"],100)
            self.assertGreater(result["inserted_samples"],90)
            self.assertFalse(result["bluetooth_radio_used"])
            con=open_db(path)
            try:
                count=con.execute("SELECT COUNT(*) FROM sensor_readings WHERE source='continuous-simulator'").fetchone()[0]
                self.assertEqual(count,result["inserted_samples"])
            finally:
                con.close()

if __name__=="__main__":
    unittest.main()
