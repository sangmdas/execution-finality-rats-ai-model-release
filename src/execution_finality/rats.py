from __future__ import annotations

import hashlib
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from .state import SQLiteExtractionState


@dataclass(frozen=True)
class ReleaseControlClaims:
    release_control_profile: str
    release_control_enabled: bool
    release_control_measurement: str
    model_identity: str
    release_policy_id: str
    security_epoch: int
    extraction_state_id: str
    extraction_state_commitment: str
    rollback_protection: bool
    finality_sink_id: str
    finality_sink_class: str
    destination_binding_supported: bool
    authority_consumption_mode: str
    alternate_egress_control: bool
    release_control_assurance: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def software_reference_claims(
    *, state: SQLiteExtractionState, scope_key: str, release_class: str,
    model_id: str, policy_id: str, sink_id: str = "python-software-sink-01",
) -> ReleaseControlClaims:
    s = state.read(scope_key, release_class)
    commitment_input = json.dumps(
        {"scope_key": scope_key, "release_class": release_class, "epoch": s["epoch"], "consumed": s["consumed"], "budget": s["budget"]},
        sort_keys=True, separators=(",", ":"),
    ).encode()
    commitment = "sha256:" + hashlib.sha256(commitment_input).hexdigest()
    package_dir = Path(__file__).resolve().parent
    mh = hashlib.sha256()
    for source in sorted(package_dir.glob("*.py")):
        mh.update(source.name.encode("utf-8"))
        mh.update(b"\x00")
        mh.update(source.read_bytes())
        mh.update(b"\x00")
    measurement = "sha256:" + mh.hexdigest()
    model_identity = model_id if model_id.startswith("sha256:") else "label:" + model_id
    return ReleaseControlClaims(
        release_control_profile="model-state-finality-reference-v1",
        release_control_enabled=True,
        release_control_measurement=measurement,
        model_identity=model_identity,
        release_policy_id=policy_id,
        security_epoch=int(s["epoch"]),
        extraction_state_id=f"sqlite:{scope_key}:{release_class}",
        extraction_state_commitment=commitment,
        rollback_protection=False,
        finality_sink_id=sink_id,
        finality_sink_class="SOFTWARE_API_EGRESS",
        destination_binding_supported=True,
        authority_consumption_mode="ATOMIC_STATE_CONSUMPTION",
        alternate_egress_control=False,
        release_control_assurance="SOFTWARE_REFERENCE",
    )
