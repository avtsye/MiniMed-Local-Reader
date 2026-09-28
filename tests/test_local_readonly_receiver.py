import json,socket,tempfile,threading,unittest
from pathlib import Path
from transport.local_readonly_receiver import LocalReadOnlyReceiver,parse_stream_line
from protocol.raw_capture import replay

class LocalReceiverTests(unittest.TestCase):
    def test_parse_and_localhost_guard(self):
        ch,data,meta=parse_stream_line('{"channel":"cgm_measurement","hex":"0102"}')
        self.assertEqual((ch,data),("cgm_measurement",bytes([1,2])))
        with self.assertRaises(ValueError):LocalReadOnlyReceiver("x.jsonl","0.0.0.0",0)

    def test_stream_is_captured(self):
        with tempfile.TemporaryDirectory() as d:
            cap=Path(d)/"raw.jsonl"
            server=LocalReadOnlyReceiver(cap)
            t=threading.Thread(target=server.serve_forever,daemon=True); t.start()
            try:
                with socket.create_connection(server.address,timeout=2) as s:
                    f=s.makefile("rwb")
                    msg=json.dumps({"channel":"history_record","hex":"0CF00102"})+"\n"
                    f.write(msg.encode()); f.flush()
                    reply=json.loads(f.readline())
                    self.assertTrue(reply["ok"])
                rows=list(replay(cap))
                self.assertEqual(rows[0]["channel"],"history_record")
                self.assertEqual(rows[0]["data"],bytes.fromhex("0CF00102"))
            finally:
                server.shutdown(); server.server_close(); t.join(timeout=2)

if __name__=="__main__": unittest.main()
