import argparse
import json

from protocol.readonly_gate import Operation
from storage.db import open_db
from transport.simulator import SimulatorTransport
from transport.windows_winrt import WindowsWinRTTransport


def main():
    parser = argparse.ArgumentParser(
        description="MiniMed Local Reader - safe Windows/read-only POC"
    )
    parser.add_argument("--probe-windows", action="store_true")
    parser.add_argument("--test-gatt", action="store_true")
    parser.add_argument("--scan-test", action="store_true")
    parser.add_argument("--discover-ble", action="store_true")
    parser.add_argument("--monitor-ble", action="store_true")
    parser.add_argument("--mobile-emulator", action="store_true")
    parser.add_argument("--emulator-client", action="store_true")
    parser.add_argument("--loopback-test", action="store_true")
    parser.add_argument("--pipeline-test", action="store_true")
    parser.add_argument("--session-demo", action="store_true")
    parser.add_argument("--seconds", type=int, default=15)
    parser.add_argument("--simulate", action="store_true")
    parser.add_argument("--db", default="minimed_local.sqlite")
    args = parser.parse_args()

    selected = (
        args.probe_windows,
        args.test_gatt,
        args.scan_test,
        args.discover_ble,
        args.monitor_ble,
        args.mobile_emulator,
        args.emulator_client,
        args.loopback_test,
        args.session_demo,
        args.simulate,
    )
    if not any(selected):
        print("MiniMed Local Reader - Windows POC")
        print("Safety mode: READ-ONLY / diagnostics; pump protocol is disabled.")
        print()
        print("Run one of:")
        print("  python app.py --probe-windows")
        print("  python app.py --test-gatt")
        print("  python app.py --scan-test")
        print("  python app.py --discover-ble")
        print("  python app.py --monitor-ble")
        print("  python app.py --mobile-emulator")
        print("  python app.py --emulator-client")
        print("  python app.py --loopback-test")
        print("  python app.py --pipeline-test")
        print("  python app.py --session-demo")
        print("  python app.py --simulate")
        return

    if args.probe_windows:
        print(json.dumps(WindowsWinRTTransport().probe(), indent=2, ensure_ascii=False))

    if args.test_gatt:
        from transport.windows_gatt_test import run as run_gatt
        print("Starting local test-only GATT advertisement...")
        print(json.dumps(run_gatt(args.seconds), indent=2, ensure_ascii=False))

    if args.scan_test:
        from transport.windows_test_scanner import run as run_scan
        print("Scanning only for the project-owned GATT test UUID...")
        print(json.dumps(run_scan(args.seconds), indent=2, ensure_ascii=False))

    if args.session_demo:
        from protocol.session_simulator import run_demo
        print("Running local read-only session simulator...")
        print(json.dumps(run_demo(args.db), indent=2, ensure_ascii=False))

    if args.pipeline_test:
        from protocol.data_pipeline import run as run_pipeline
        print("Running simulated end-to-end data pipeline...")
        print(json.dumps(run_pipeline(args.db), indent=2, ensure_ascii=False))

    if args.loopback_test:
        from transport.emulator_loopback import run as run_loopback
        print("Running single-computer software loopback (no Bluetooth radio)...")
        print(json.dumps(run_loopback(args.db), indent=2, ensure_ascii=False))

    if args.emulator_client:
        from transport.windows_emulator_client import run as run_emulator_client
        print("Connecting only to the project-owned BLE emulator (read-only)...")
        print(json.dumps(run_emulator_client(args.seconds), indent=2, ensure_ascii=False))

    if args.mobile_emulator:
        from transport.windows_mobile_emulator import run as run_mobile_emulator
        print("Starting project-owned Mobile-side BLE emulator (read-only)...")
        print(json.dumps(run_mobile_emulator(args.seconds, args.db), indent=2, ensure_ascii=False))

    if args.monitor_ble:
        from transport.windows_ble_monitor import run as run_monitor
        print("Passive BLE signal monitor (no pairing/connections/writes)...")
        print(json.dumps(run_monitor(args.seconds), indent=2, ensure_ascii=False))

    if args.discover_ble:
        from transport.windows_ble_client import run as run_discovery
        print("Passive BLE discovery (no connections/writes)...")
        print(json.dumps(run_discovery(args.seconds), indent=2, ensure_ascii=False))

    if args.simulate:
        transport = SimulatorTransport()
        transport.connect()
        try:
            for name in ("read_device_info", "read_status", "read_cgm", "read_history"):
                print(name, transport.execute(Operation(name)).decode())
        finally:
            transport.disconnect()
        connection = open_db(args.db)
        connection.close()


if __name__ == "__main__":
    main()
