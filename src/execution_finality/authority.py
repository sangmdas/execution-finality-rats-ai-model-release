from __future__ import annotations

import uuid
from .crypto import HMACAuthenticator
from .models import CandidateRelease, ReleaseAuthority, Reservation


def _authority_fields(
    *, authority_id: str, reservation_id: str, candidate_digest: str,
    model_id: str, release_class: str, destination: str, epoch: int,
    scope_key: str, quantity: int,
) -> dict[str, object]:
    return {
        "authority_id": authority_id,
        "reservation_id": reservation_id,
        "candidate_digest": candidate_digest,
        "model_id": model_id,
        "release_class": release_class,
        "destination": destination,
        "epoch": epoch,
        "scope_key": scope_key,
        "quantity": quantity,
        "profile": "execution-finality-release-authority-v1",
    }


class ReleaseAuthorityIssuer:
    def __init__(self, authenticator: HMACAuthenticator) -> None:
        self.authenticator = authenticator

    def issue(self, candidate: CandidateRelease, candidate_digest: str, reservation: Reservation) -> ReleaseAuthority:
        a = candidate.attributes
        authority_id = str(uuid.uuid4())
        fields = _authority_fields(
            authority_id=authority_id,
            reservation_id=reservation.reservation_id,
            candidate_digest=candidate_digest,
            model_id=a.model_id,
            release_class=a.release_class,
            destination=a.destination,
            epoch=a.epoch,
            scope_key=a.scope_key,
            quantity=a.quantity,
        )
        return ReleaseAuthority(mac=self.authenticator.sign(fields), **{k: fields[k] for k in fields if k != "profile"})

    def verify(self, authority: ReleaseAuthority) -> bool:
        fields = _authority_fields(
            authority_id=authority.authority_id,
            reservation_id=authority.reservation_id,
            candidate_digest=authority.candidate_digest,
            model_id=authority.model_id,
            release_class=authority.release_class,
            destination=authority.destination,
            epoch=authority.epoch,
            scope_key=authority.scope_key,
            quantity=authority.quantity,
        )
        return self.authenticator.verify(fields, authority.mac)
