"""Localhost-only receiver for externally established read-only byte streams."""
import json
import socketserver
from pathlib import Path
from transport.external_readonly_sink import ExternalReadOnlyByteSink

MAX_LINE=1024*1024

def parse_stream_line(line):
    if len(line)>MAX_LINE: raise ValueError("input line too large")
    row=json.loads(line)
    channel=row.get("channel"); hex_data=row.get("hex")
    if not isinstance(channel,str) or not channel: raise ValueError("channel is required")
    if not isinstance(hex_data,str): raise ValueError("hex is required")
    try:data=bytes.fromhex(hex_data)
    except ValueError as e: raise ValueError("invalid hex") from e
    metadata=row.get("metadata") or {}
    if not isinstance(metadata,dict): raise ValueError("metadata must be an object")
    return channel,data,metadata

class _Handler(socketserver.StreamRequestHandler):
    def handle(self):
        sink=self.server.sink
        while True:
            raw=self.rfile.readline(MAX_LINE+1)
            if not raw: break
            try:
                channel,data,metadata=parse_stream_line(raw.decode("utf-8"))
                sink.accept_received_bytes(channel,data,metadata)
                reply={"ok":True,"bytes":len(data)}
            except Exception as e:
                reply={"ok":False,"error":str(e)}
            self.wfile.write((json.dumps(reply,separators=(",",":"))+"\n").encode("utf-8"))
            self.wfile.flush()

class LocalReadOnlyReceiver(socketserver.ThreadingTCPServer):
    allow_reuse_address=True
    daemon_threads=True
    def __init__(self,capture_path,host="127.0.0.1",port=0):
        if host not in ("127.0.0.1","localhost","::1"):
            raise ValueError("receiver is localhost-only")
        self.sink=ExternalReadOnlyByteSink(Path(capture_path))
        super().__init__((host,port),_Handler)

    @property
    def address(self):
        return self.server_address
