import argparse, json
from protocol.readonly_gate import Operation
from transport.simulator import SimulatorTransport
from transport.windows_winrt import WindowsWinRTTransport
from storage.db import open_db

def main():
    p = argparse.ArgumentParser(description="MiniMed Local Reader - safe Windows/read-only POC")
    p.add_argument("--probe-windows", action="store_true", help="Check Windows BLE/WinRT capabilities")
    p.add_argument("--test-gatt", action="store_true", help="Advertise a project-owned local GATT test service")
    p.add_argument("--scan-test", action="store_true", help="Scan only for the project-owned test service UUID")
    p.add_argument("--seconds", type=int, default=15, help="Duration for --test-gatt (1-120 seconds)")
    p.add_argument("--simulate", action="store_true", help="Run the local read-only simulator")
    p.add_argument("--db", default="minimed_local.sqlite")
    args = p.parse_args()

    if not args.probe_windows and not args.simulate and not args.test_gatt and not args.scan_test:
        print("MiniMed Local Reader - Windows POC")
        print("Safety mode: READ-ONLY / diagnostics; pump protocol is disabled.")
        print()
        print("Run one of:")
        print("  python app.py --probe-windows")
        print("  python app.py --test-gatt")\n        print("  python app.py --scan-test")
        print("  python app.py --simulate")
        return

    if args.probe_windows:
        print(json.dumps(WindowsWinRTTransport().probe(), indent=2, ensure_ascii=False))

    if args.test_gatt:
        from transport.windows_gatt_test import run
        print("Starting local test-only GATT advertisement...")
        print(json.dumps(run(args.seconds), indent=2, ensure_ascii=False))

    if args.scan_test:
        from transport.windows_test_scanner import run as run_scan
        print("Scanning only for the project-owned GATT test UUID...")
        print(json.dumps(run_scan(args.seconds), indent=2, ensure_ascii=False))

    if args.simulate:
        t = SimulatorTransport(); t.connect()
        for name in ("read_device_info", "read_status", "read_cgm", "read_history"):
            print(name, t.execute(Operation(name)).decode())
        t.disconnect()
        con = open_db(args.db); con.close()

if __name__ == "__main__":
    main()
