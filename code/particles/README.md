# Compact Particle Export

This directory is the public-facing export of the active sibling
`/particles` workspace. It is rebuilt as a compact surface for papers, the
book, and the repo README, without copying the Oracle batch archive,
automation plumbing, or sandbox process history.

## Layout

- `core/`: compatibility backbone for the current public predictor modules
  that newer lanes still depend on.
- `calibration/`: D10 and D11 exactness-audit lane.
- `flavor/`: shared charged-sector, projector, transport, and quark
  continuation lane.
- `leptons/`: charged-lepton continuation lane.
- `neutrino/`: forward neutrino continuation lane and guards.
- `hadron/`: debug/systematics hadron lane, including baryon and
  `rho`-scattering scaffolds.
- `runs/`: frozen current public artifacts.
- `RESULTS_STATUS.md`, `results_status.json`, `ledger.yaml`: compact status
  surfaces for the current public claim boundary.

## Intentional Boundary

This export keeps the current scientific code and frozen current outputs. It
does not mirror:

- Oracle prompts, batch manifests, or transcripts
- autonomous supervisor tooling
- browser-profile or launchd setup
- quantum sandbox utilities
- planning docs, work trackers, and long run history

## Public Status

- `D10`: calibration closure lane
- `D11`: secondary quantitative Higgs/top lane
- charged leptons, flavor, neutrinos: continuation lanes with explicit
  artifact boundaries
- hadrons: simulation-dependent debug lane only

The presence of code or artifacts here is not a promotion of those lanes to
theorem-level OPH output.

Some rows in `RESULTS_STATUS.md` still miss experiment, in some sectors by a
large margin. That is expected at the current public boundary. In `D10` and
`D11`, the remaining mismatch is being treated as a missing transport/readout
closure problem rather than a mere decimal-precision issue in `P`. In the
charged, flavor, and neutrino lanes, the remaining error sits behind still-open
shared-scale, family-excitation, and selector/evaluator objects. In hadrons,
the current numbers come from a debug/systematics lane and are not closure
candidates. Further work is ongoing on exactly those missing objects.

## Minimal Dependencies

```bash
pip install -r code/particles/requirements.txt
```

## Useful Checks

```bash
python3 code/particles/calibration/test_single_p_consistency.py
python3 code/particles/calibration/test_d10_observable_family_artifact.py
python3 code/particles/flavor/test_flavor_dictionary_disambiguation.py
python3 code/particles/leptons/test_ratio_only_not_promoted.py
python3 code/particles/neutrino/test_bundle_descent_candidate_fields.py
python3 code/particles/tests/test_hadron_demo_not_promoted.py
```
