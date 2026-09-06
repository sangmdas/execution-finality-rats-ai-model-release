from __future__ import annotations

from dataclasses import dataclass
from .models import ReleaseAttributes


@dataclass(frozen=True)
class ReleasePolicy:
    policy_id: str
    model_id: str
    allowed_release_classes: frozenset[str]
    allowed_destinations: frozenset[str]
    allowed_principals: frozenset[str]
    epoch: int

    def allows(self, attrs: ReleaseAttributes) -> tuple[bool, str]:
        if attrs.policy_id != self.policy_id:
            return False, "policy_id_mismatch"
        if attrs.model_id != self.model_id:
            return False, "model_mismatch"
        if attrs.epoch != self.epoch:
            return False, "stale_or_wrong_epoch"
        if attrs.release_class not in self.allowed_release_classes:
            return False, "release_class_denied"
        if attrs.destination not in self.allowed_destinations:
            return False, "destination_denied"
        if attrs.principal_id not in self.allowed_principals:
            return False, "principal_denied"
        return True, "allowed"
