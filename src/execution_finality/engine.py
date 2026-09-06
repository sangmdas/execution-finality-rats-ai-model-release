from __future__ import annotations

from dataclasses import dataclass
from .authority import ReleaseAuthorityIssuer
from .crypto import digest_candidate
from .models import CandidateRelease, ReleaseAuthority
from .policy import ReleasePolicy
from .sink import FinalitySink, ReleaseResult, SinkVerificationError
from .state import SQLiteExtractionState, StateError


class ReleaseDenied(RuntimeError):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True)
class PreparedRelease:
    candidate: CandidateRelease
    authority: ReleaseAuthority


class ExecutionFinalityEngine:
    def __init__(
        self,
        *, policy: ReleasePolicy,
        state: SQLiteExtractionState,
        issuer: ReleaseAuthorityIssuer,
        sink: FinalitySink,
    ) -> None:
        self.policy = policy
        self.state = state
        self.issuer = issuer
        self.sink = sink

    def prepare(self, candidate: CandidateRelease) -> PreparedRelease:
        allowed, reason = self.policy.allows(candidate.attributes)
        if not allowed:
            raise ReleaseDenied(reason)

        digest = digest_candidate(candidate.attributes.as_mapping(), candidate.payload)
        try:
            reservation = self.state.reserve(
                scope_key=candidate.attributes.scope_key,
                release_class=candidate.attributes.release_class,
                epoch=candidate.attributes.epoch,
                quantity=candidate.attributes.quantity,
                candidate_digest=digest,
            )
            authority = self.issuer.issue(candidate, digest, reservation)
            self.state.attach_authority(reservation.reservation_id, authority.authority_id)
            return PreparedRelease(candidate, authority)
        except StateError as e:
            raise ReleaseDenied(str(e)) from e

    def release_prepared(self, prepared: PreparedRelease) -> ReleaseResult:
        try:
            return self.sink.effect_release(prepared.candidate, prepared.authority)
        except (SinkVerificationError, StateError) as e:
            raise ReleaseDenied(str(e)) from e

    def attempt(self, candidate: CandidateRelease) -> ReleaseResult:
        return self.release_prepared(self.prepare(candidate))
