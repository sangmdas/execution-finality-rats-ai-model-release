from __future__ import annotations

from dataclasses import dataclass
from .authority import ReleaseAuthorityIssuer
from .crypto import digest_candidate
from .models import CandidateRelease, ReleaseAuthority
from .state import SQLiteExtractionState, InvalidReservation


class SinkVerificationError(RuntimeError):
    pass


@dataclass(frozen=True)
class ReleaseResult:
    payload: bytes
    authority_id: str
    reservation_id: str


class FinalitySink:
    """
    First governed boundary in this software reference at which payload bytes are returned.

    This protects only calls that traverse this object. It cannot stop a privileged host
    from reading the same plaintext from another memory/API path; that is why the default
    assurance profile does not claim alternate-egress closure.
    """

    def __init__(self, state: SQLiteExtractionState, authority_issuer: ReleaseAuthorityIssuer) -> None:
        self.state = state
        self.authority_issuer = authority_issuer

    def verify(self, candidate: CandidateRelease, authority: ReleaseAuthority) -> None:
        if not self.authority_issuer.verify(authority):
            raise SinkVerificationError("authority authentication failed")

        digest = digest_candidate(candidate.attributes.as_mapping(), candidate.payload)
        a = candidate.attributes
        expected = {
            "candidate_digest": digest,
            "model_id": a.model_id,
            "release_class": a.release_class,
            "destination": a.destination,
            "epoch": a.epoch,
            "scope_key": a.scope_key,
            "quantity": a.quantity,
        }
        actual = {
            "candidate_digest": authority.candidate_digest,
            "model_id": authority.model_id,
            "release_class": authority.release_class,
            "destination": authority.destination,
            "epoch": authority.epoch,
            "scope_key": authority.scope_key,
            "quantity": authority.quantity,
        }
        if actual != expected:
            raise SinkVerificationError("authority is not bound to this Candidate Release")

        r = self.state.reservation(authority.reservation_id)
        if r["status"] != "RESERVED":
            raise SinkVerificationError("reservation is not live (replay/stale/terminal)")
        if r["authority_id"] != authority.authority_id:
            raise SinkVerificationError("authority is not attached to this reservation")
        if r["candidate_digest"] != digest:
            raise SinkVerificationError("reservation candidate digest mismatch")
        if r["epoch"] != a.epoch:
            raise SinkVerificationError("reservation epoch mismatch")

        current = self.state.read(a.scope_key, a.release_class)
        if current["epoch"] != a.epoch:
            raise SinkVerificationError("authority is stale after a protected security-epoch transition")

    def effect_release(self, candidate: CandidateRelease, authority: ReleaseAuthority) -> ReleaseResult:
        self.verify(candidate, authority)
        # Conservative reference behavior: terminally consume before returning bytes.
        # This prevents replay/double release at the cost of possible budget loss if the
        # process crashes after commit but before the caller receives the return value.
        try:
            self.state.commit(authority.reservation_id, authority.authority_id)
        except InvalidReservation as e:
            raise SinkVerificationError(str(e)) from e
        return ReleaseResult(candidate.payload, authority.authority_id, authority.reservation_id)
