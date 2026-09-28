import tempfile
import unittest
from pathlib import Path
from datasource.synthetic import SyntheticDataSource
from datasource.ingest import ingest_once
from storage.db import open_db

class ReadOnlyDataSourceTests(unittest.TestCase):
    def test_ingest_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"source.sqlite"
            source=SyntheticDataSource()
            result=ingest_once(source,path)
            self.assertTrue(result["ingest_completed"])
            self.assertFalse(result["writes_enabled"])
            con=open_db(path)
            try:
                self.assertEqual(con.execute("SELECT COUNT(*) FROM sensor_readings").fetchone()[0],1)
                self.assertEqual(con.execute("SELECT COUNT(*) FROM device_status").fetchone()[0],1)
            finally: con.close()

    def test_unsafe_source_is_rejected(self):
        class Unsafe(SyntheticDataSource):
            def capabilities(self):
                x=super().capabilities(); x["writes"]=True; return x
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(RuntimeError): ingest_once(Unsafe(),Path(d)/"x.sqlite")

if __name__=="__main__": unittest.main()
