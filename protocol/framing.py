"""Offline packet framing/reassembly helpers.

Generic length-prefixed framing for captured/replayed test streams. This module
does not describe or transmit a pump command protocol.
"""
class LengthPrefixedReassembler:
    def __init__(self,max_frame=65535):
        self.buffer=bytearray(); self.max_frame=max_frame

    def feed(self,chunk):
        self.buffer.extend(bytes(chunk)); out=[]
        while len(self.buffer)>=2:
            size=int.from_bytes(self.buffer[:2],"little")
            if size>self.max_frame: raise ValueError("frame exceeds configured maximum")
            if len(self.buffer)<2+size: break
            out.append(bytes(self.buffer[2:2+size]))
            del self.buffer[:2+size]
        return out

def frame(payload):
    payload=bytes(payload)
    if len(payload)>65535: raise ValueError("payload too large")
    return len(payload).to_bytes(2,"little")+payload
