from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any
import base64


@dataclass(frozen=True)
class ReleaseAttributes:
    """Load-bearing attributes committed by a Candidate Release."""

    model_id: str
    workload_id: str
    principal_id: str
    release_class: str
    destination: str
    quantity: int
    policy_id: str
    epoch: int
    nonce: str
    scope_key: str

    def __post_init__(self) -> None:
        for name in (
            "model_id", "workload_id", "principal_id", "release_class",
            "destination", "policy_id", "nonce", "scope_key"
        ):
            if not getattr(self, name):
                raise ValueError(f"{name} must be non-empty")
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
        if self.epoch < 0:
            raise ValueError("epoch must be non-negative")

    def as_mapping(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CandidateRelease:
    """A proposed release. Construction does not authorize external effect."""

    attributes: ReleaseAttributes
    payload: bytes

    def payload_b64(self) -> str:
        return base64.b64encode(self.payload).decode("ascii")


@dataclass(frozen=True)
class Reservation:
    reservation_id: str
    scope_key: str
    release_class: str
    candidate_digest: str
    quantity: int
    epoch: int
    status: str


@dataclass(frozen=True)
class ReleaseAuthority:
    """Bound authority; possession alone is insufficient without matching context."""

    authority_id: str
    reservation_id: str
    candidate_digest: str
    model_id: str
    release_class: str
    destination: str
    epoch: int
    scope_key: str
    quantity: int
    mac: str
