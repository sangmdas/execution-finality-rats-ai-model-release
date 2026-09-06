# Engineering FAQ — Non-Repetitive Performance and Deployment Questions

## Does atomic consumption create a global serialization bottleneck?
No global counter is required. Atomicity is scoped to authority that could otherwise be double-spent. State can be sharded or delegated into non-overlapping bounded allowances.

## Must the finality procedure execute on every token-generation step?
No. Internal decoding is computation. Finality applies to the chosen externally effective release boundary.

## Does this break streaming inference?
No. A bounded stream/chunk can be a Candidate Release unit. The stream's authority must remain bounded by class, destination, epoch, quantity, and state.

## Does every release require a persistent hardware write?
No. Rollback resistance is a property. The persistence/checkpoint/epoch mechanism is profile-specific.

## Does every release require a public-key signature?
No. Local MACs, protected handles, authenticated device-local state, or other mechanisms can implement bounded authority inside a trust domain.

## Does the design add a CPU/GPU round trip per protected release?
Not inherently. Validation/state/sink functions can be colocated in firmware, TEE, accelerator, DPU, or another protected boundary.

## What about continuous batching and microbatching?
Compute scheduling and release authorization are independent. Requests can share a compute batch while retaining separate authority scopes.

## What about tensor, pipeline, expert, or disaggregated inference?
Internal transfers inside one protected domain are not automatically external releases. A transfer becomes a Candidate Release when it crosses the deployment's relevant protected-to-less-trusted boundary.

## Can fail-closed behavior create service-wide outages?
It should be scoped. Failure of one extraction-state shard or authority domain should not automatically stop unrelated ordinary outputs, tenants, models, or independent release scopes.

## What if validation cannot keep up?
The control stage can be sharded, colocated, parallelized, or delegated. Overload must not silently become default-allow.

## Does KV-cache protection require an extra copy?
No. A Finality Sink is a logical role and may be enforced at an existing memory, DMA, interconnect, API, or network boundary.

## What should performance benchmarks disclose?
At minimum: Candidate Release granularity, assurance class, protected-release throughput, added latency, accelerator utilization, contention, concurrency scaling, batching behavior, and failure-path cost.
