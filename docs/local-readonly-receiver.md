# Local read-only receiver

A connector that already has an established data stream can send received bytes
to MiniMed Local Reader over a localhost TCP socket.

Each line is JSON:

    {"channel":"cgm_measurement","hex":"06007B000000","metadata":{}}

The server replies with one JSON line acknowledging accepted byte count or an
input-validation error.

Security properties:
- binds only to loopback addresses;
- never scans, pairs, handshakes, or writes to a BLE device;
- accepts received bytes only;
- preserves bytes in the normal raw-capture format before decoding.
