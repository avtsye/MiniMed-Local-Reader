"""Passive BLE discovery -> lifecycle/logger bridge."""
from protocol.ble_logger import log_event
from protocol.ble_state import BleSessionState, BleState
from protocol.physical_ble_guard import safety_status
from storage.db import open_db
from transport.windows_ble_client import run as discover

def run(seconds=10, db_path="minimed_local.sqlite", max_devices=50):
    state=BleSessionState(); con=open_db(db_path)
    try:
        state.transition(BleState.DISCOVERING)
        log_event(con,"ble_discovery_started",{"seconds":seconds})
        result=discover(seconds,max_devices); devices=result.get("devices",[])
        for device in devices:
            log_event(con,"ble_advertisement_observed",{
                "bluetooth_address":device.get("bluetooth_address"),
                "bluetooth_address_type":device.get("bluetooth_address_type"),
                "rssi":device.get("rssi"),
                "local_name":device.get("local_name",""),
                "service_uuids":device.get("service_uuids",[]),
                "manufacturer_data":device.get("manufacturer_data",[]),
                "data_sections":device.get("data_sections",[]),
            })
        if devices:
            state.transition(BleState.CANDIDATE_FOUND,address=devices[0].get("bluetooth_address"))
            log_event(con,"ble_candidate_observed",{
                "bluetooth_address":state.candidate_address,
                "selection_reason":"strongest advertisement in this passive scan only",
            })
        state.transition(BleState.DISCONNECTED)
        log_event(con,"ble_discovery_finished",{"device_count":len(devices)})
        return {"discovery_completed":True,"state":state.state.value,"device_count":len(devices),
                "candidate_address":state.candidate_address,"candidate_is_identified_pump":False,
                "connection_attempted":False,**safety_status()}
    except Exception as exc:
        try: log_event(con,"ble_discovery_failed",{"error":f"{type(exc).__name__}: {exc}"})
        except Exception: pass
        return {"discovery_completed":False,"state":state.state.value,"connection_attempted":False,
                "reason":f"{type(exc).__name__}: {exc}",**safety_status()}
    finally: con.close()
