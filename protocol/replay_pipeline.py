"""Offline replay pipeline for already-captured packets."""
from protocol.raw_capture import replay
from protocol.cgm_decoder import decode_cgm_measurement
from protocol.history_decoder import decode_history_envelope
from protocol.framing import LengthPrefixedReassembler

def decode_replay(path):
    out=[]; assemblers={}
    for row in replay(path):
        channel=row["channel"]; data=row["data"]
        if channel=="cgm_measurement":
            out.append({"channel":channel,"decoded":decode_cgm_measurement(data,bool(row.get("metadata",{}).get("use_crc",False)))})
        elif channel=="history_record":
            out.append({"channel":channel,"decoded":decode_history_envelope(data)})
        elif channel.startswith("framed:"):
            key=channel.split(":",1)[1]
            asm=assemblers.setdefault(key,LengthPrefixedReassembler())
            for payload in asm.feed(data):
                out.append({"channel":key,"decoded":{"payload_hex":payload.hex().upper()}})
        else:
            out.append({"channel":channel,"decoded":{"payload_hex":data.hex().upper()}})
    return out
