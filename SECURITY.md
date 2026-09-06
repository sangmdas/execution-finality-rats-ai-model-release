# Security Policy for the Reference Implementation

This code is intentionally a **software reference**, not a production security boundary.

Do not use the default HMAC key handling, SQLite state store, process-local policy engine, or Python Finality Sink as evidence of hardware-enforced alternate-egress closure.

Security-sensitive production replacements should consider:

- attested TEE/confidential-computing or accelerator-firmware enforcement;
- hardware/firmware-protected rollback-resistant state;
- device assignment and DMA/IOMMU controls;
- debugger/telemetry/peer-device egress closure;
- key isolation and rotation;
- measured boot/reference values/endorsements;
- distributed state delegation and reconciliation;
- crash/uncertain-effect semantics;
- side-channel and covert-channel analysis.

Please report implementation defects privately to the repository maintainer before public exploitation details are posted.
