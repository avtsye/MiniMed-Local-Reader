import json,tempfile,unittest
from pathlib import Path
from datasource.pythonpumpconnector_import import import_connector_jsonl,export_contract

class ConnectorImportTests(unittest.TestCase):
    def test_import_cgm_export(self):
        with tempfile.TemporaryDirectory() as d:
            src=Path(d)/"external.jsonl"; cap=Path(d)/"capture.jsonl"
            src.write_text(json.dumps({"channel":"cgm_measurement","hex":"06007B000000"})+"\n",encoding="utf-8")
            x=import_connector_jsonl(src,cap)
            self.assertEqual(x["imported"],1)
            self.assertEqual(x["decoded"][0]["decoded"]["glucose"],123.0)
            self.assertFalse(export_contract()["active_device_control"])

    def test_invalid_hex_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            src=Path(d)/"bad.jsonl"
            src.write_text(json.dumps({"channel":"cgm_measurement","hex":"ZZ"})+"\n",encoding="utf-8")
            with self.assertRaises(ValueError):import_connector_jsonl(src,Path(d)/"c.jsonl")

if __name__=="__main__": unittest.main()
