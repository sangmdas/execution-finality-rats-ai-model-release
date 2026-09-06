from __future__ import annotations

import unittest
from dataclasses import replace

from execution_finality.engine import ReleaseDenied, PreparedRelease
from execution_finality.models import CandidateRelease
from execution_finality.state import SQLiteExtractionState
from common import candidate, fixture


class SecurityTests(unittest.TestCase):
    def test_allow_path_consumes_budget(self):
        td, db, state, engine = fixture(budget=2)
        try:
            result = engine.attempt(candidate("a"))
            self.assertEqual(result.payload, b"secret-smi")
            self.assertEqual(state.read("model-17:partner", "HIGH_RES_LOGPROBS")["consumed"], 1)
        finally:
            state.close(); td.cleanup()

    def test_exhaustion_fails_closed(self):
        td, db, state, engine = fixture(budget=1)
        try:
            engine.attempt(candidate("a"))
            with self.assertRaises(ReleaseDenied):
                engine.attempt(candidate("b"))
        finally:
            state.close(); td.cleanup()

    def test_wrong_destination_denied_before_reservation(self):
        td, db, state, engine = fixture(budget=2)
        try:
            with self.assertRaises(ReleaseDenied):
                engine.attempt(candidate("a", destination="tenant:evil"))
            self.assertEqual(state.read("model-17:partner", "HIGH_RES_LOGPROBS")["consumed"], 0)
        finally:
            state.close(); td.cleanup()

    def test_stale_epoch_denied(self):
        td, db, state, engine = fixture()
        try:
            with self.assertRaises(ReleaseDenied):
                engine.attempt(candidate("a", epoch=6))
        finally:
            state.close(); td.cleanup()

    def test_replay_of_consumed_authority_denied(self):
        td, db, state, engine = fixture(budget=2)
        try:
            prepared = engine.prepare(candidate("a"))
            engine.release_prepared(prepared)
            with self.assertRaises(ReleaseDenied):
                engine.release_prepared(prepared)
        finally:
            state.close(); td.cleanup()

    def test_payload_tamper_after_authority_issue_denied(self):
        td, db, state, engine = fixture(budget=2)
        try:
            prepared = engine.prepare(candidate("a", payload=b"original"))
            tampered = CandidateRelease(prepared.candidate.attributes, b"tampered")
            forged = PreparedRelease(tampered, prepared.authority)
            with self.assertRaises(ReleaseDenied):
                engine.release_prepared(forged)
        finally:
            state.close(); td.cleanup()

    def test_attribute_tamper_after_authority_issue_denied(self):
        td, db, state, engine = fixture(budget=2)
        try:
            prepared = engine.prepare(candidate("a"))
            attrs = replace(prepared.candidate.attributes, destination="tenant:evil")
            tampered = CandidateRelease(attrs, prepared.candidate.payload)
            with self.assertRaises(ReleaseDenied):
                engine.release_prepared(PreparedRelease(tampered, prepared.authority))
        finally:
            state.close(); td.cleanup()

    def test_process_restart_does_not_reset_sqlite_budget(self):
        td, db, state, engine = fixture(budget=1)
        try:
            engine.attempt(candidate("a"))
            state.close()
            reopened = SQLiteExtractionState(db)
            try:
                self.assertEqual(reopened.read("model-17:partner", "HIGH_RES_LOGPROBS")["remaining"], 0)
            finally:
                reopened.close()
        finally:
            td.cleanup()

    def test_tampered_authority_mac_denied(self):
        td, db, state, engine = fixture(budget=2)
        try:
            prepared = engine.prepare(candidate("mac"))
            bad = replace(prepared.authority, mac="00" * 32)
            with self.assertRaises(ReleaseDenied):
                engine.release_prepared(PreparedRelease(prepared.candidate, bad))
        finally:
            state.close(); td.cleanup()

    def test_authority_invalid_after_state_epoch_transition(self):
        td, db, state, engine = fixture(budget=2)
        try:
            prepared = engine.prepare(candidate("epoch-transition"))
            # Security-relevant maintenance/policy transition advances protected state.
            state.provision("model-17:partner", "HIGH_RES_LOGPROBS", 8, 2)
            with self.assertRaises(ReleaseDenied):
                engine.release_prepared(prepared)
        finally:
            state.close(); td.cleanup()

    def test_quantity_is_enforced_against_budget(self):
        td, db, state, engine = fixture(budget=2)
        try:
            with self.assertRaises(ReleaseDenied):
                engine.attempt(candidate("quantity", quantity=3))
            self.assertEqual(state.read("model-17:partner", "HIGH_RES_LOGPROBS")["consumed"], 0)
        finally:
            state.close(); td.cleanup()


if __name__ == "__main__":
    unittest.main()
