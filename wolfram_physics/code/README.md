# Code

This directory has two code surfaces.

## Toy Benchmark

These files reconstruct the toy benchmark used by
`papers/observer_consistent_semantic_quotients_for_the_ruliad.tex`.

- `ruliad_toy_benchmark.py`
- `test_ruliad_toy_benchmark.py`
- `ruliad_toy_benchmark_results.json`

From `reverse-engineering-reality/wolfram_physics/`, run:

```bash
python3 code/ruliad_toy_benchmark.py
python3 code/test_ruliad_toy_benchmark.py
```

## Survivor Bridge Package

The follow-up theorem package lives under:

- `followup_survivor_bridge/src/`
- `followup_survivor_bridge/tests/`
- `followup_survivor_bridge/data/`
- `followup_survivor_bridge/results/`

This package starts from the 8-class toy semantic quotient and studies defect vectors, deterministic nearest-improvement dynamics, minimal survivor sectors, and primitive noisy kernels on the minimal sector.

From `reverse-engineering-reality/wolfram_physics/`, run:

```bash
python3 code/followup_survivor_bridge/src/survivor_bridge.py
python3 code/followup_survivor_bridge/tests/test_survivor_bridge.py
```

The toy benchmark computes the reported counts and exits non-zero on mismatch. The survivor bridge package uses the computed semantic quotient as its input artifact.
