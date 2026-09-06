from __future__ import annotations

import unittest
from common import fixture
from execution_finality.rats import software_reference_claims


class RatsClaimsTests(unittest.TestCase):
    def test_software_reference_does_not_overclaim_hardware_assurance(self):
        td, db, state, engine = fixture()
        try:
            claims = software_reference_claims(
                state=state, scope_key="model-17:partner", release_class="HIGH_RES_LOGPROBS",
                model_id="model-17", policy_id="policy-17",
            )
            self.assertTrue(claims.release_control_enabled)
            self.assertFalse(claims.rollback_protection)
            self.assertFalse(claims.alternate_egress_control)
            self.assertEqual(claims.release_control_assurance, "SOFTWARE_REFERENCE")
        finally:
            state.close(); td.cleanup()


if __name__ == "__main__":
    unittest.main()
