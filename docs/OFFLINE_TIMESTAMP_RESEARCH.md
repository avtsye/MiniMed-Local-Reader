# Offline timestamp research

CareLink Uploader 3.15.0 static class inspection identified `HistoryPoint`,
`NGPHistoryPoint` and `NGPTimestamp`. The NGP implementation references
the Unix timestamp 946684800 (2000-01-01 00:00:00 UTC).

This is **not** evidence that MiniMed 700/780G data uses the same encoding.

`protocol.offline_timestamp.inspect_ngp_timestamp` is an opt-in, offline-only
research utility for already-exported data. It assumes RTC and offset are
integer seconds relative to the 2000 epoch. Do not use its output for medical
decisions, treatment, alerts, or automated insulin delivery.

The utility does not open Bluetooth, connect to a pump, pair devices, issue
commands, or write to any device. Tests use synthetic timestamps only.

Next: compare against non-identifying timestamps from a supported CareLink
export and document whether the hypothesis holds before integration.
