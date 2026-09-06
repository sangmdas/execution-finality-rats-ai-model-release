from __future__ import annotations

import json
import os
import tempfile
from .authority import ReleaseAuthorityIssuer
from .crypto import HMACAuthenticator
from .engine import ExecutionFinalityEngine, ReleaseDenied
from .models import CandidateRelease, ReleaseAttributes
from .policy import ReleasePolicy
from .rats import software_reference_claims
from .sink import FinalitySink
from .state import SQLiteExtractionState


def make_candidate(*, nonce: str, destination: str = "tenant:acme", epoch: int = 7, quantity: int = 1, payload: bytes = b"privileged-logprob-vector") -> CandidateRelease:
    return CandidateRelease(
        attributes=ReleaseAttributes(
            model_id="model-frontier-17",
            workload_id="workload-serving-04",
            principal_id="partner-eval",
            release_class="HIGH_RES_LOGPROBS",
            destination=destination,
            quantity=quantity,
            policy_id="policy-frontier-17",
            epoch=epoch,
            nonce=nonce,
            scope_key="model-frontier-17:partner-eval",
        ),
        payload=payload,
    )


def build_engine(db_path: str, budget: int = 2):
    state = SQLiteExtractionState(db_path)
    state.provision("model-frontier-17:partner-eval", "HIGH_RES_LOGPROBS", 7, budget)
    policy = ReleasePolicy(
        policy_id="policy-frontier-17",
        model_id="model-frontier-17",
        allowed_release_classes=frozenset({"HIGH_RES_LOGPROBS"}),
        allowed_destinations=frozenset({"tenant:acme"}),
        allowed_principals=frozenset({"partner-eval"}),
        epoch=7,
    )
    # DEMO ONLY. Production keys belong in the protected enforcement domain.
    issuer = ReleaseAuthorityIssuer(HMACAuthenticator(b"D" * 32))
    sink = FinalitySink(state, issuer)
    return ExecutionFinalityEngine(policy=policy, state=state, issuer=issuer, sink=sink), state


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        db = os.path.join(td, "extraction-state.sqlite3")
        engine, state = build_engine(db, budget=2)

        print("== Execution-Finality reference demo ==")
        print("Computation may occur; release is separate authority.\n")

        c1 = make_candidate(nonce="n-001")
        r1 = engine.attempt(c1)
        print("ALLOW 1:", r1.payload.decode())

        prepared = engine.prepare(make_candidate(nonce="n-002"))
        r2 = engine.release_prepared(prepared)
        print("ALLOW 2:", r2.payload.decode())

        for label, candidate in [
            ("EXHAUSTED", make_candidate(nonce="n-003")),
            ("WRONG DESTINATION", make_candidate(nonce="n-004", destination="tenant:evil")),
            ("STALE EPOCH", make_candidate(nonce="n-005", epoch=6)),
        ]:
            try:
                engine.attempt(candidate)
                print(label, "UNEXPECTED ALLOW")
            except ReleaseDenied as e:
                print(label, "DENY:", e.reason)

        try:
            engine.release_prepared(prepared)
            print("REPLAY UNEXPECTED ALLOW")
        except ReleaseDenied as e:
            print("REPLAY DENY:", e.reason)

        print("\nRATS-style illustrative claim set (software assurance only):")
        claims = software_reference_claims(
            state=state,
            scope_key="model-frontier-17:partner-eval",
            release_class="HIGH_RES_LOGPROBS",
            model_id="model-frontier-17",
            policy_id="policy-frontier-17",
        )
        print(json.dumps(claims.as_dict(), indent=2, sort_keys=True))
        state.close()


if __name__ == "__main__":
    main()
