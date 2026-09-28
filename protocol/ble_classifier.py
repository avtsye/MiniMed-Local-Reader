"""Passive BLE advertisement classifier.

Produces descriptive evidence only. It does not identify a pump, connect,
pair, access GATT, or enable any protocol.
"""
import json
from collections import defaultdict
from storage.db import open_db
from protocol.physical_ble_guard import safety_status

def classify(db_path="minimed_local.sqlite", limit=2000):
    con=open_db(db_path)
    try:
        rows=con.execute(
            "SELECT event_time,payload_json FROM pump_events "
            "WHERE source='physical-ble-infrastructure' AND event_type='ble_advertisement_observed' "
            "ORDER BY id DESC LIMIT ?", (int(limit),)
        ).fetchall()
    finally:
        con.close()

    grouped=defaultdict(lambda:{
        "observations":0,"rssi_values":[],"local_names":set(),
        "service_uuids":set(),"manufacturer_company_ids":set(),"data_types":set()
    })
    for _,raw in rows:
        try: item=json.loads(raw)
        except Exception: continue
        address=item.get("bluetooth_address")
        if not address: continue
        g=grouped[address]; g["observations"]+=1
        if isinstance(item.get("rssi"),(int,float)): g["rssi_values"].append(item["rssi"])
        if item.get("local_name"): g["local_names"].add(item["local_name"])
        g["service_uuids"].update(item.get("service_uuids") or [])
        for m in item.get("manufacturer_data") or []:
            if "company_id" in m:g["manufacturer_company_ids"].add(m["company_id"])
        for s in item.get("data_sections") or []:
            if "data_type" in s:g["data_types"].add(s["data_type"])

    candidates=[]
    for address,g in grouped.items():
        rssi=g.pop("rssi_values")
        evidence=[]
        if g["service_uuids"]: evidence.append("advertises service UUID(s)")
        if g["manufacturer_company_ids"]: evidence.append("contains manufacturer data")
        if g["data_types"]: evidence.append("contains BLE data sections")
        if g["local_names"]: evidence.append("advertises local name")
        candidates.append({
            "bluetooth_address":address,
            "observations":g["observations"],
            "rssi":{"min":min(rssi),"max":max(rssi),"avg":round(sum(rssi)/len(rssi),1)} if rssi else None,
            "local_names":sorted(g["local_names"]),
            "service_uuids":sorted(g["service_uuids"]),
            "manufacturer_company_ids":sorted(g["manufacturer_company_ids"]),
            "data_types":sorted(g["data_types"]),
            "descriptive_evidence":evidence,
            "identified_as_pump":False,
        })
    candidates.sort(key=lambda x:(x["observations"],len(x["descriptive_evidence"])),reverse=True)
    return {
        "classification":"descriptive-passive-evidence-only",
        "candidate_count":len(candidates),
        "candidates":candidates,
        "connection_attempted":False,
        **safety_status(),
    }
