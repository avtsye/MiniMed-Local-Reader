"""Conservative offline history-record envelope decoder.

The upstream project contains many event-specific parsers. Here we first port
the safe envelope/catalog layer: classify known event type identifiers and
preserve the remaining bytes losslessly for later offline decoders.
"""
KNOWN_EVENT_TYPES={
0x000F:"REFERENCE_TIME",0x005A:"BOLUS_PROGRAMMED_P1",0x0066:"BOLUS_PROGRAMMED_P2",
0x0069:"BOLUS_DELIVERED_P1",0x0096:"BOLUS_DELIVERED_P2",0x0099:"DELIVERED_BASAL_RATE_CHANGED",
0xF001:"AUTO_BASAL_DELIVERY",0xF002:"CL1_TRANSITION",0xF004:"THERAPY_CONTEXT",
0xF005:"MEAL",0xF007:"BG_READING",0xF008:"CALIBRATION_COMPLETE",0xF009:"CALIBRATION_REJECTED",
0xF00A:"INSULIN_DELIVERY_STOPPED",0xF00B:"INSULIN_DELIVERY_RESTARTED",0xF00C:"SG_MEASUREMENT",
0xF00D:"CGM_ANALYTICS_DATA_BACKFILL",0xF00E:"NGP_REFERENCE_TIME",0xF00F:"ANNUNCIATION_CLEARED",
0xF010:"ANNUNCIATION_CONSOLIDATED",0xF01A:"MAX_AUTO_BASAL_RATE_CHANGED",
}

def decode_history_envelope(data):
    raw=bytes(data)
    if len(raw)<2: raise ValueError("history record too short")
    event_type=int.from_bytes(raw[:2],"little")
    return {"event_type":event_type,"event_name":KNOWN_EVENT_TYPES.get(event_type,"UNDEFINED"),
            "payload_hex":raw[2:].hex().upper(),"raw_hex":raw.hex().upper()}
