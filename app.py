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
    parser.add_argument(
        "--probe-windows",
        action="store_true",
        help="Check Windows BLE/WinRT capabilities",
    )
    parser.add_argument(
        "--test-gatt",
        action="store_true",
        help="Advertise a project-owned local GATT test service",
    )
    parser.add_argument(
        "--scan-test",
        action="store_true",
        help="Scan only for the project-owned test service UUID",
    )
    parser.add_argument(
        "--seconds",
        type=int,
        default=15,
        help="Duration for BLE diagnostics (1-120 seconds)",
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Run the local read-only simulator",
    )
    parser.add_argument("--db", default="minimed_local.sqlite")
    args = parser.parse_args()

    if not any(
        (args.probe_windows, args.test_gatt, args.scan_test, args.discover_ble, args.simulate)
    ):
        print("MiniMed Local Reader - Windows POC")
        print("Safety mode: READ-ONLY / diagnostics; pump protocol is disabled.")
        print()
        print("Run one of:")
        print("  python app.py --probe-windows")
        print("  python app.py --test-gatt")
        print("  python app.py --scan-test")\n        print("  python app.py --discover-ble")
        print("  python app.py --simulate")
        return

    if args.probe_windows:
        print(
            json.dumps(
                WindowsWinRTTransport().probe(),
                indent=2,
                ensure_ascii=False,
            )
        )

    if args.test_gatt:
        from transport.windows_gatt_test import run as run_gatt

        print("Starting local test-only GATT advertisement...")
        print(
            json.dumps(
                run_gatt(args.seconds),
                indent=2,
                ensure_ascii=False,
            )
        )

    if args.discover_ble:
        from transport.windows_ble_client import run as run_discovery

        print("Passive BLE discovery (no connections/writes)...")
        print(
            json.dumps(
                run_discovery(args.seconds),
                indent=2,
                ensure_ascii=False,
            )
        )

    if args.scan_test:
        from transport.windows_test_scanner import run as run_scan

        print("Scanning only for the project-owned GATT test UUID...")
        print(
            json.dumps(
                run_scan(args.seconds),
                indent=2,
                ensure_ascii=False,
            )
        )

    if args.simulate:
        transport = SimulatorTransport()
        transport.connect()
        try:
            for name in (
                "read_device_info",
                "read_status",
                "read_cgm",
                "read_history",
            ):
                print(name, transport.execute(Operation(name)).decode())
        finally:
            transport.disconnect()

        connection = open_db(args.db)
        connection.close()


if __name__ == "__main__":
    main()
