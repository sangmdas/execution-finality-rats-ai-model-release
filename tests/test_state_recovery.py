from __future__ import annotations

import unittest
from common import candidate, fixture
from execution_finality.crypto import digest_candidate
from execution_finality.state import InvalidReservation


class RecoveryTests(unittest.TestCase):
    def test_cancel_no_effect_restores_capacity_only_while_reserved(self):
        td, db, state, engine = fixture(budget=1)
        try:
            c = candidate("x")
            d = digest_candidate(c.attributes.as_mapping(), c.payload)
            r = state.reserve(scope_key=c.attributes.scope_key, release_class=c.attributes.release_class, epoch=c.attributes.epoch, quantity=1, candidate_digest=d)
            self.assertEqual(state.read(c.attributes.scope_key, c.attributes.release_class)["remaining"], 0)
            state.cancel_no_effect(r.reservation_id)
            self.assertEqual(state.read(c.attributes.scope_key, c.attributes.release_class)["remaining"], 1)
            with self.assertRaises(InvalidReservation):
                state.cancel_no_effect(r.reservation_id)
        finally:
            state.close(); td.cleanup()


if __name__ == "__main__":
    unittest.main()
