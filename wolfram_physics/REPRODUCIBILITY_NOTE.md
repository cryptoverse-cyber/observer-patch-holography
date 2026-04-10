# Reproducibility Note

This note covers the toy benchmark reported in [Observer-Consistent Semantic Quotients for the Ruliad](papers/observer_consistent_semantic_quotients_for_the_ruliad.pdf).

From `reverse-engineering-reality/wolfram_physics/`, run:

```bash
python3 code/ruliad_toy_benchmark.py
python3 code/test_ruliad_toy_benchmark.py
```

These commands reproduce the reported toy counts:

- `raw rule families = 154`
- `semantic classes = 8`
- `after confluence = 103`
- `after holonomy = 92`
- `total rejected = 62`
- `surviving semantic classes = 2`

This code reconstructs the toy benchmark. It does not serve as a formal verification of every mathematical claim in the paper.

The script fixes the benchmark conventions explicitly:

- the toy edge set, depth cutoff, and family sizes
- the history convention: all rooted paths from `E` of lengths `0..3`
- the two consistent packet states
- the repair rule: nearest consistent packet in Hamming distance with `ell`-preserving tie-break
- the confluence filter: all reachable histories repair to the same packet normal form
- the holonomy filter: every reachable history has vanishing cycle sum
- the toy finite-constraint stage as reporting-only, with no extra exclusion threshold beyond the first two filters

The published totals appear in the script for post-computation verification only. The enumeration and grouping logic compute the counts first and compare afterward.
