# Contributing

Contributions should preserve the architecture's separation between **computation** and **authority to release**.

A change that makes the happy path faster by introducing default-allow behavior, reusable generic bearer authority, rollback-recreatable budget, or an unverified alternate release path is not compatible with the reference security model.

For substantial changes, include tests for:

1. allow path;
2. denial path;
3. replay/tamper behavior;
4. stale epoch;
5. concurrency where shared authority is consumed;
6. crash or terminal-state behavior where relevant.

Do not upgrade an attestation/assurance claim merely because a software feature exists. The claim must reflect the actual enforcement boundary.
