"""Physical transport boundary.

This object documents the exact point where an externally supplied, approved
read-only byte stream can enter the decoder pipeline. It deliberately contains
no code for pairing, session handshakes, characteristic writes, or commands.
"""
from protocol.raw_capture import RawPacketRecorder

class ExternalReadOnlyByteSink:
    def __init__(self,capture_path):
        self.recorder=RawPacketRecorder(capture_path)

    def accept_received_bytes(self,channel,data,metadata=None):
        return self.recorder.record(channel,bytes(data),metadata)

    def write(self,*args,**kwargs):
        raise RuntimeError("Physical-device writes are not implemented")

    def pair(self,*args,**kwargs):
        raise RuntimeError("Physical-device pairing is not implemented")

    def handshake(self,*args,**kwargs):
        raise RuntimeError("Physical-device handshake is not implemented")
