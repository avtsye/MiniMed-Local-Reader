"""Offline decoder for Bluetooth SIG CGM Measurement records.

Input must already be plaintext bytes. No BLE connection, decryption, pairing,
control-point operation, or device command is implemented here.
"""
import math
import struct

def _sfloat(raw):
    value=int.from_bytes(raw,"little")
    mantissa=value & 0x0FFF
    exponent=(value >> 12) & 0x0F
    if mantissa >= 0x0800: mantissa -= 0x1000
    if exponent >= 0x08: exponent -= 0x10
    return mantissa * (10 ** exponent)

def decode_cgm_measurement(data,use_crc=False):
    data=bytes(data)
    minimum=8 if use_crc else 6
    if len(data)<minimum: raise ValueError("CGM record too short")
    declared=data[0]
    if declared != len(data): raise ValueError("CGM record size mismatch")
    body=data[:-2] if use_crc else data
    flags=body[1]
    glucose=_sfloat(body[2:4])
    offset=int.from_bytes(body[4:6],"little")
    pos=6
    result={"flags":flags,"glucose":float(glucose),"time_offset_minutes":offset,
            "status":0,"cal_temp":0,"warning":0,"trend":None,"quality":None}
    for mask,key in ((0x80,"status"),(0x40,"cal_temp"),(0x20,"warning")):
        if flags & mask:
            if pos>=len(body): raise ValueError("CGM optional octet truncated")
            result[key]=body[pos]; pos+=1
    for mask,key in ((0x01,"trend"),(0x02,"quality")):
        if flags & mask:
            if pos+2>len(body): raise ValueError("CGM optional SFLOAT truncated")
            result[key]=float(_sfloat(body[pos:pos+2])); pos+=2
    if pos != len(body): raise ValueError("Unexpected trailing CGM bytes")
    return result
