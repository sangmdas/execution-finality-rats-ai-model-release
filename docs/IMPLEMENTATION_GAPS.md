# Implementation Gaps Requiring Profile-Specific Engineering

The source draft deliberately leaves several production questions open. This repository does not hide them.

## 1. Crash / uncertain external effect

Exactly-once external effect is not generally obtained from a local database transaction plus an unrelated remote/network effect. The reference profile chooses consume-before-return, which gives at-most-once behavior on its in-process return path but can sacrifice availability.

Production profiles need explicit reservation, acknowledgement, poison, timeout, recovery, and durable ordering semantics.

## 2. Multi-device / multi-region extraction state

This repository uses one SQLite state domain. Production systems may use non-overlapping delegated allowances, sharded state, protected coordinator services, or another distributed mechanism. The invariant is that the same bounded authority cannot be independently recreated/spent in two domains.

## 3. Hardware rollback resistance

SQLite persistence is not protection against disk/VM snapshot rollback by a sufficiently privileged operator. A stronger profile needs trusted monotonic/epoch state, sealed storage tied to freshness, or another anti-rollback mechanism.

## 4. Alternate-egress closure

The Python sink controls only code paths that call it. Production systems need a closure argument for host-visible memory, DMA, PCIe, peer-device transfer, debuggers, telemetry, shared memory, storage, and network interfaces carrying equivalent SMI.

## 5. Destination identity

The demo uses a canonical string such as `tenant:acme`. A production profile must define whether destination binding is a workload identity, tenant identity, public key, protected channel binding, attested receiver, service identity, or another security-domain identifier.

## 6. Attestation profile and freshness

The `rats.py` claims are illustrative. A real profile must define claim syntax/semantics, Evidence/Attestation Result placement, reference values, freshness, epoch relation, endorsement appraisal, privacy exposure, and interoperability behavior.

## 7. Side/covert channels

Execution finality over governed release paths does not alone remove side channels, covert channels, malicious firmware, or equivalent ungoverned information channels.
