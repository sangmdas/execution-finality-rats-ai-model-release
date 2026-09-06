from __future__ import annotations

import concurrent.futures
import unittest
from common import candidate, fixture
from execution_finality.engine import ReleaseDenied


class ConcurrencyTests(unittest.TestCase):
    def test_only_one_thread_gets_final_budget_unit(self):
        td, db, state, engine = fixture(budget=1)
        try:
            def attempt(i):
                try:
                    engine.attempt(candidate(f"c-{i}"))
                    return "ALLOW"
                except ReleaseDenied:
                    return "DENY"

            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(attempt, range(8)))
            self.assertEqual(results.count("ALLOW"), 1)
            self.assertEqual(results.count("DENY"), 7)
            self.assertEqual(state.read("model-17:partner", "HIGH_RES_LOGPROBS")["consumed"], 1)
        finally:
            state.close(); td.cleanup()


if __name__ == "__main__":
    unittest.main()
