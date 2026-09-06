# Legacy and Incremental Deployment

The architecture can be introduced without changing externally visible application API names.

## Stage 1 — software gateway

Existing inference services classify privileged exports and apply release-specific authorization, destination binding, replay protection, and extraction-state accounting.

**Assurance:** useful semantics, weak alternate-egress closure.

## Stage 2 — TEE / confidential-computing enforcement

Move policy state, validation, keys, and release decisions into an attested protected execution environment.

**Assurance:** stronger host-compromise resistance, but device/DMA/firmware paths still require analysis.

## Stage 3 — accelerator / protected firmware enforcement

Move release state and sink verification close to accelerator egress, protected DMA, memory/interconnect, or device API boundaries.

**Assurance:** stronger closure against driver/host bypass.

## Stage 4 — silicon-backed primitives

Use dedicated primitives for atomic consumption, protected monotonic/epoch state, model-bound state, egress verification, and trustworthy evidence generation.

**Assurance:** potentially strongest, dependent on implementation and appraisal evidence.

## Important

A software gateway and a silicon-backed sink may expose similar logical semantics but **must not advertise the same RATS assurance class**.
