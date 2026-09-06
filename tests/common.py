from __future__ import annotations

import os
import tempfile
from execution_finality.authority import ReleaseAuthorityIssuer
from execution_finality.crypto import HMACAuthenticator
from execution_finality.engine import ExecutionFinalityEngine
from execution_finality.models import CandidateRelease, ReleaseAttributes
from execution_finality.policy import ReleasePolicy
from execution_finality.sink import FinalitySink
from execution_finality.state import SQLiteExtractionState


def candidate(nonce: str, *, destination="tenant:acme", epoch=7, quantity=1, payload=b"secret-smi", model_id="model-17", principal="partner"):
    return CandidateRelease(
        ReleaseAttributes(
            model_id=model_id,
            workload_id="workload-1",
            principal_id=principal,
            release_class="HIGH_RES_LOGPROBS",
            destination=destination,
            quantity=quantity,
            policy_id="policy-17",
            epoch=epoch,
            nonce=nonce,
            scope_key="model-17:partner",
        ),
        payload,
    )


def fixture(budget=3):
    td = tempfile.TemporaryDirectory()
    db = os.path.join(td.name, "state.sqlite3")
    state = SQLiteExtractionState(db)
    state.provision("model-17:partner", "HIGH_RES_LOGPROBS", 7, budget)
    policy = ReleasePolicy(
        policy_id="policy-17", model_id="model-17",
        allowed_release_classes=frozenset({"HIGH_RES_LOGPROBS"}),
        allowed_destinations=frozenset({"tenant:acme"}),
        allowed_principals=frozenset({"partner"}), epoch=7,
    )
    issuer = ReleaseAuthorityIssuer(HMACAuthenticator(b"K"*32))
    sink = FinalitySink(state, issuer)
    engine = ExecutionFinalityEngine(policy=policy, state=state, issuer=issuer, sink=sink)
    return td, db, state, engine
