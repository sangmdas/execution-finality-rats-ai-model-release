# Execution-Finality for Protected AI Model-State Release

**Runnable reference implementation accompanying the architecture described in**
`draft-das-rats-openai-anthropic-extraction`.

> Core rule: **computation is not authority to release**.

This repository demonstrates a software reference implementation of the following logical chain:

```text
Model computation
    -> Candidate Release (non-effective)
    -> Protected Validation
    -> rollback/replay-aware Extraction State
    -> atomic reservation/consumption
    -> bounded non-bearer Release Authority
    -> Finality Sink verification
    -> externally usable release or fail-closed denial
```

It is deliberately written so that an engineer can run it, attack it, inspect the state transitions, and replace individual software components with TEE, confidential-GPU, firmware, DPU/SmartNIC, protected-DMA, interconnect, or silicon-backed equivalents.

## What this repository is — and is not

This is a **reference implementation of the architecture's semantics**, not a claim that ordinary Python and SQLite provide the same assurance as an attested TEE, protected accelerator firmware, or silicon-backed egress controller.

The default RATS-style claim set therefore reports:

- `release_control_assurance = SOFTWARE_REFERENCE`
- `rollback_protection = false` for hardware/anti-rollback assurance
- `alternate_egress_control = false`

The demo *does* provide process-crash-persistent state, atomic database transactions, replay protection, destination/model/epoch binding, bounded authority, concurrency tests, and fail-closed behavior for the governed software path. See [docs/ASSURANCE_LEVELS.md](docs/ASSURANCE_LEVELS.md).

## Quick start

Requires Python 3.11+ and no third-party runtime packages.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .
execution-finality-demo
python -m unittest discover -s tests -v
```

Or without installation:

```bash
PYTHONPATH=src python -m execution_finality.demo
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Expected demo behavior

The demonstration provisions a model/release-class budget, performs one authorized protected release, then exercises stale-epoch, wrong-destination, replay, and exhausted-budget denials. Denied Candidate Releases never become externally usable through the governed `FinalitySink` method.

## Repository map

```text
src/execution_finality/
  models.py          canonical Candidate Release and Release Authority models
  crypto.py          HMAC reference authenticator and canonical hashing
  policy.py          explicit release policy / release-class gating
  state.py           SQLite-backed extraction state + atomic reservation
  authority.py       bounded non-bearer authority issuer/verifier
  sink.py            Finality Sink and fail-closed release path
  engine.py          end-to-end orchestration
  rats.py            illustrative RATS/EAT-style release-control claims
  demo.py            runnable demonstration
  benchmark.py       local overhead microbenchmark (not a vendor benchmark)

tests/
  security and concurrency tests

docs/
  architecture, threat model, performance, legacy deployment,
  RATS mapping, assurance levels, implementation gaps, references

docs/reference/
  source Internet-Draft XML supplied with this repository
```

## Security properties represented

The implementation maps directly to the draft's desired properties:

| Property | Reference implementation |
|---|---|
| R1 computation/release separation | payload is held in `CandidateRelease` until sink succeeds |
| R2 release-specific binding | authority authenticates canonical model/release/destination/epoch/digest attributes |
| R3 rollback resistance | **partial only**: SQLite survives process restart; hardware/VM rollback resistance is not claimed |
| R4 atomic reservation/consumption | SQLite `BEGIN IMMEDIATE` transaction protects final budget unit |
| R5 replay resistance | reservation and authority IDs become consumed/terminal |
| R6 alternate-path closure | **not claimed by software demo**; deployment requirement documented |
| R7 fail-closed controlled release | verification failure returns denial and no governed-path payload |
| R8 attestable enforcement state | illustrative claim generator; not a real EAT attester |

## Performance design — what is *not* inherently required

The architecture does **not inherently require**:

- a remote attestation round trip for every Candidate Release;
- a remote policy call per generated token;
- a non-volatile hardware counter write per token;
- a globally serialized extraction counter;
- a public-key signature for every token;
- a CPU/GPU round trip for every token;
- treating speculative tokens, expert routing, internal tensors, or every decode step as external releases.

This repository's SQLite state store is intentionally easy to audit, not a performance prescription. A production implementation can replace it with sharded protected state, accelerator-local bounded allocations, TEE-local state, firmware primitives, or other mechanisms while preserving the same invariants. See [docs/PERFORMANCE.md](docs/PERFORMANCE.md).

## Conservative crash semantics

The reference sink uses an **at-most-once, consume-before-return** strategy for the final governed return path. Once an authority is committed, a crash before the caller receives the bytes may consume budget without delivering data. This is an availability tradeoff, not an exactly-once guarantee. It is chosen because silently recreating authority after an uncertain effect is the more dangerous failure for this security objective.

Production protocols may implement reservation/commit/poison/recovery semantics closer to the draft, but must define their external-effect acknowledgement boundary precisely. See [docs/IMPLEMENTATION_GAPS.md](docs/IMPLEMENTATION_GAPS.md).

## IPR / licensing note

This repository does not define patent licensing terms. The accompanying Internet-Draft states that IPR disclosures are handled separately through the applicable IETF IPR process. **No patent license should be inferred from the presence of this reference implementation.**

No permissive software license is bundled in this archive; absent a separate license from the rights holder, ordinary copyright rules apply.

## Reference

The supplied source document is retained unchanged at:

`docs/reference/draft-das-rats-openai-anthropic-extraction-01.xml`

See [docs/REFERENCES.md](docs/REFERENCES.md) for the architecture's cited RATS/EAT and related work.
