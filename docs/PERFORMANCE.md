# Performance and AI-Throughput Notes

The reference implementation is designed for **scrutiny of semantics**, not to prescribe Python/SQLite on an AI inference hot path.

## Performance invariants

Execution finality does not inherently require:

1. remote attestation per token or Candidate Release;
2. remote policy calls per decode step;
3. a globally serialized counter;
4. a physical non-volatile write per token;
5. a public-key signature per token;
6. a CPU/GPU transition per token;
7. treating internal speculative tokens, tensor-parallel traffic, expert routing, KV movement, or every generated token as an external effect.

## Slow path vs fast path

Slow path candidates include initial/periodic platform attestation, policy provisioning, key establishment, model registration, epoch initialization, and budget delegation.

Fast path enforcement can remain local to a protected accelerator, firmware, TEE, protected host-device boundary, DPU/SmartNIC, memory/interconnect controller, or equivalent protected role.

## No required global serialization

Atomicity is required **only where the same authority could otherwise be spent twice**. Production deployments can shard state by model, tenant, requester, release class, destination, epoch, accelerator, or non-overlapping delegated allowance.

## Streaming

Streaming need not be disabled. A bounded stream or stream chunk can be the Candidate Release unit. A profile can authorize a maximum quantity/class/destination/epoch and consume the bounded allowance incrementally.

## Continuous batching / microbatching

The accelerator scheduling unit and the authorization unit are separate. Multiple Candidate Releases may share one compute batch while retaining distinct release scopes.

## Tensor/pipeline/MoE parallelism

Internal transfers inside one protected execution domain are not automatically external releases. Finality applies at the boundary where protected information becomes usable by a less-trusted or independently authorized domain.

## Persistent state

Rollback resistance is a security property, not an instruction to increment TPM/NVRAM for every token. Production replacements may use protected local epochs, sealed checkpoints, bounded delegation, protected firmware state, or other anti-rollback constructions.

## Microbenchmark

`python -m execution_finality.benchmark` measures only this Python/SQLite reference path. Results must **not** be cited as GPU, TEE, DPU, firmware, or silicon performance.
