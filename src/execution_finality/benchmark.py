from __future__ import annotations

import os
import statistics
import tempfile
import time
from .demo import build_engine, make_candidate


def main(iterations: int = 1000) -> None:
    """Microbenchmark for local Python/SQLite path only; not a vendor latency claim."""
    with tempfile.TemporaryDirectory() as td:
        db = os.path.join(td, "bench.sqlite3")
        engine, state = build_engine(db, budget=iterations + 10)
        samples_us = []
        start_all = time.perf_counter_ns()
        for i in range(iterations):
            c = make_candidate(nonce=f"bench-{i}")
            t0 = time.perf_counter_ns()
            engine.attempt(c)
            samples_us.append((time.perf_counter_ns() - t0) / 1000.0)
        elapsed_s = (time.perf_counter_ns() - start_all) / 1e9
        samples_us_sorted = sorted(samples_us)
        p50 = statistics.median(samples_us)
        p95 = samples_us_sorted[int(0.95 * (len(samples_us_sorted)-1))]
        p99 = samples_us_sorted[int(0.99 * (len(samples_us_sorted)-1))]
        print("REFERENCE SOFTWARE MICROBENCHMARK -- NOT A GPU/TEE PERFORMANCE CLAIM")
        print(f"iterations: {iterations}")
        print(f"throughput: {iterations/elapsed_s:,.1f} governed releases/s")
        print(f"p50: {p50:,.1f} us  p95: {p95:,.1f} us  p99: {p99:,.1f} us")
        print("SQLite + Python are chosen for auditability. Production profiles may fuse/shard/colocate operations.")
        state.close()


if __name__ == "__main__":
    main()
