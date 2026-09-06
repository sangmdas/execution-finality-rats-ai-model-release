# RATS / EAT Mapping

The repository separates two objects:

1. **attestation information** about the presence/state/assurance of release control; and
2. **act-specific bounded Release Authority** used on a particular governed release path.

They are intentionally not conflated.

## Illustrative claim semantics implemented in `rats.py`

- `release_control_profile`
- `release_control_enabled`
- `release_control_measurement`
- `model_identity`
- `release_policy_id`
- `security_epoch`
- `extraction_state_id`
- `extraction_state_commitment`
- `rollback_protection`
- `finality_sink_id`
- `finality_sink_class`
- `destination_binding_supported`
- `authority_consumption_mode`
- `alternate_egress_control`
- `release_control_assurance`

The code does **not** encode these as registered EAT/CWT claim numbers and does not pretend to be a conforming EAT profile. They remain illustrative semantics matching the source architecture.

## Why the default claims are conservative

The Python process cannot prove that DMA, debugger, telemetry, peer-GPU, or privileged-host paths are subordinate to it. It also cannot provide hardware-backed VM snapshot rollback resistance. Therefore those claims are false in the default profile.

A production Attesting Environment should only assert stronger values when its Evidence and measured components support them and the Verifier has appropriate Reference Values, Endorsements, and appraisal policy.
