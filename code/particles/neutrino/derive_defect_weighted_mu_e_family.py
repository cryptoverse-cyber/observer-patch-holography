#!/usr/bin/env python3
"""Export the defect-weighted Majorana edge-weight family candidate."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCALAR = ROOT /  "runs" / "neutrino" / "majorana_overlap_defect_scalar_evaluator.json"
DEFAULT_FORWARD = ROOT /  "runs" / "neutrino" / "forward_neutrino_closure_bundle.json"
DEFAULT_OUT = ROOT /  "runs" / "neutrino" / "defect_weighted_mu_e_family.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the defect-weighted mu_e family artifact.")
    parser.add_argument("--scalar", default=str(DEFAULT_SCALAR))
    parser.add_argument("--forward", default=str(DEFAULT_FORWARD))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    scalar = json.loads(Path(args.scalar).read_text(encoding="utf-8"))
    forward = json.loads(Path(args.forward).read_text(encoding="utf-8"))
    masses = [float(x) for x in forward.get("masses_gev_sorted", [])]
    m0 = sum(masses[:2]) / 2.0 if len(masses) >= 2 else None
    heavy_light_gap = (masses[2] - m0) if len(masses) >= 3 and m0 is not None else None
    mu_nu = float(scalar.get("mu_nu", 0.0))

    artifact = {
        "artifact": "oph_defect_weighted_majorana_edge_weight_family",
        "generated_utc": _timestamp(),
        "parent_theorem_id": scalar.get("theorem_candidate_id"),
        "upstream_exact_clause": scalar.get("required_overlap_certificate"),
        "normalizer_artifact": "oph_same_label_overlap_defect_weight_normalizer",
        "selector_center": scalar.get("selector_center"),
        "selector_point_absolute": scalar.get("selector_point_absolute"),
        "kernel_choice": "1-cos",
        "base_mu_nu": mu_nu,
        "raw_defect_source": scalar.get("overlap_nonvanishing_witness_hint"),
        "defect_log_centered": {"psi12": None, "psi23": None, "psi31": None},
        "weight_rule": "mu_e = base_mu_nu * exp(delta_e) / mean_f(exp(delta_f))",
        "edge_weights": {"psi12": None, "psi23": None, "psi31": None},
        "residual_hessian_formula_2x2": [
            ["mu12 + mu31", "mu31"],
            ["mu31", "mu23 + mu31"],
        ],
        "mean_preserved": True,
        "positive_weights": True,
        "isotropic_limit_recovered": True,
        "current_doublet_center_gev": m0,
        "current_heavy_light_gap_gev": heavy_light_gap,
        "current_delta_m21_sq_gev2": forward.get("delta_m21_sq_gev2"),
        "current_delta_m31_sq_gev2": forward.get("delta_m31_sq_gev2"),
        "delta_m21_sq_expected_status": "strictly_positive_for_generic_nonconstant_delta",
        "ordering_expected_status": "normal_like_stable_for_small_defect_anisotropy",
        "proof_status": "candidate_only",
        "notes": [
            "This is the first local mass-moving object that can lift the current 1-2 near-degeneracy without changing the centered selector, kernel choice, or edge-character origin candidate.",
            "The exact theorem blocker remains on same-label overlap / edge-bundle normalization, but the smallest spectrum-moving local object is the positive overlap-defect weight normalizer that turns raw defect data into centered additive edge logs.",
        ],
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
