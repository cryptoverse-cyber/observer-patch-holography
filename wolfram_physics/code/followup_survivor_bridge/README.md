# Follow-Up Survivor Bridge Package

This package supports the finite survivor quotient draft on observer-semantic Ruliad pruning.

Structure:

- `src/`
  Implementation of the finite-state bridge machinery.
- `tests/`
  Regression tests for the toy 8-class survivor quotient.
- `data/`
  Notes on the data dependency.
- `results/`
  Generated JSON report from the toy witness system.

The code reads the semantic quotient artifact at `code/ruliad_toy_benchmark_results.json`.

From `reverse-engineering-reality/wolfram_physics/`, run:

```bash
python3 code/followup_survivor_bridge/src/survivor_bridge.py
```

Write a JSON report with:

```bash
python3 code/followup_survivor_bridge/src/survivor_bridge.py \
  --json-out code/followup_survivor_bridge/results/toy_survivor_bridge_report.json
```

Verify with:

```bash
python3 code/followup_survivor_bridge/tests/test_survivor_bridge.py
```
