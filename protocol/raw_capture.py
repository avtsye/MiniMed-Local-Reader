"""Raw read-only packet capture/replay.

Stores bytes already received from an external transport. It does not connect,
pair, subscribe, write characteristics, or send device commands.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

class RawPacketRecorder:
    def __init__(self,path): self.path=Path(path)

    def record(self,channel,data,metadata=None):
        raw=bytes(data)
        row={"timestamp":datetime.now(timezone.utc).isoformat(),"channel":str(channel),
             "hex":raw.hex().upper(),"metadata":metadata or {}}
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.path.open("a",encoding="utf-8") as f:
            f.write(json.dumps(row,ensure_ascii=False)+"\n")
        return row

def replay(path):
    with Path(path).open("r",encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            row=json.loads(line)
            yield {**row,"data":bytes.fromhex(row["hex"])}
