# MiniMed Local Reader — Windows POC

Safety-first local reader scaffold. It currently contains **no MiniMed wire opcodes** and cannot issue therapy-changing commands.

> **Research software only.** This project is not a medical device and must not be relied on for treatment decisions or insulin delivery.

## Run simulator

```powershell
python app.py --simulate
```

## Windows capability probe

```powershell
python app.py --probe-windows
```

## Tests

```powershell
python -m unittest discover -s tests -v
```

## Current milestones

- Transport abstraction
- Simulator
- Semantic read-only allow-list
- SQLite schema
- Windows WinRT capability probe
- Local-only architecture; no CareLink/cloud integration

## Intentionally absent

- Bolus/basal/therapy control
- Pump setting changes
- Unverified pump opcodes
- CareLink/cloud integration

## Safety design

The current POC contains no real MiniMed wire opcodes. Unknown operations and therapy-related operations are blocked by the read-only authorization gate. Local SQLite databases are excluded from Git by default.

Next engineering step: implement Windows BLE advertising + local GATT service compatibility against a simulator/test peripheral, then connect verified OpenMinimed read-only protocol components.
