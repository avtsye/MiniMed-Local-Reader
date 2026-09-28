# External connector bridge

MiniMed Local Reader can consume bytes exported by a separate read-only data
collector without giving that collector access to this application's database
or UI.

JSONL contract:

    {"channel":"cgm_measurement","hex":"06007B000000"}
    {"channel":"history_record","hex":"0CF0..."}

The bridge validates hexadecimal input, records an immutable local capture, and
passes it through the existing replay/decoder pipeline.

The bridge intentionally does not start pairing, perform a session handshake,
write GATT characteristics, or issue pump commands. Those operations are not
part of MiniMed Local Reader.
