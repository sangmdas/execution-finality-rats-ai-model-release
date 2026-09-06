from __future__ import annotations

import hashlib
import hmac
import json
from typing import Mapping, Any


def canonical_json(obj: Mapping[str, Any]) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest_candidate(attributes: Mapping[str, Any], payload: bytes) -> str:
    h = hashlib.sha256()
    h.update(b"execution-finality:candidate:v1\x00")
    h.update(canonical_json(attributes))
    h.update(b"\x00")
    h.update(hashlib.sha256(payload).digest())
    return h.hexdigest()


class HMACAuthenticator:
    """Reference-only authenticator. Replace with protected keys in production."""

    def __init__(self, key: bytes) -> None:
        if len(key) < 32:
            raise ValueError("reference HMAC key must be at least 32 bytes")
        self._key = key

    def sign(self, fields: Mapping[str, Any]) -> str:
        return hmac.new(self._key, canonical_json(fields), hashlib.sha256).hexdigest()

    def verify(self, fields: Mapping[str, Any], mac_hex: str) -> bool:
        expected = self.sign(fields)
        return hmac.compare_digest(expected, mac_hex)
