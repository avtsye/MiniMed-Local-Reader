import argparse, json
from protocol.readonly_gate import Operation
from transport.simulator import SimulatorTransport
from transport.windows_winrt import WindowsWinRTTransport
from storage.db import open_db

def main():
    p = argparse.ArgumentParser(description="MiniMed Local Reader - safe Windows/read-only POC")
    p.add_argument("--probe-windows", action="store_true")
    p.add_argument("--simulate", action="store_true")
    p.add_argument("--db", default="minimed_local.sqlite")
    args = p.parse_args()

    if args.probe_windows:
        print(json.dumps(WindowsWinRTTransport().probe(), indent=2, ensure_ascii=False))
    if args.simulate:
        t = SimulatorTransport(); t.connect()
        for name in ("read_device_info", "read_status", "read_cgm", "read_history"):
            print(name, t.execute(Operation(name)).decode())
        t.disconnect()
    con = open_db(args.db); con.close()

if __name__ == "__main__": main()
