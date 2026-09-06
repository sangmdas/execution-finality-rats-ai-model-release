# Threat Model

## In scope for this software reference

- replay of already-consumed authority;
- candidate/payload tampering after authority issuance;
- destination substitution;
- stale epoch;
- over-budget release;
- concurrent double consumption of the final budget unit;
- process restart attempting to reset ordinary in-process counters;
- policy/release-class mismatch through the governed software path.

## Architectural threats documented but not fully enforced by Python

- VM/disk snapshot rollback of the SQLite database;
- privileged-host compromise;
- compromised drivers/firmware;
- DMA and PCIe bypass;
- debugger/diagnostic/telemetry bypass;
- peer-device and interconnect bypass;
- side channels and covert channels;
- attestation-key or Verifier compromise;
- distributed state desynchronization across machines/accelerators.

The software demo is intentionally explicit about these gaps rather than converting them into unverifiable claims.
