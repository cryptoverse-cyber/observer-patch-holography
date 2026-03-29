#!/usr/bin/env python3
"""Emit the honest D12 quark mass-side underdetermination theorem artifact.

Chain role: record the sharpest exact theorem the current D12 quark
continuation branch actually proves on the mass side before any theorem-grade
scale-fixing law is claimed.

Mathematics: the current same-family D12 branch fixes only the ray
``(Delta_ud_overlap, eta_Q_centered) = ray_modulus * (1/5, -((1 - x2^2) / 27))``.
That is a real structural reduction, but the branch does not honestly emit a
distinguished normalization point on that ray.

OPH-derived inputs: the scalarized D12 continuation bundle, the one-scalar
same-family specialization artifact, and the current same-family diagnostic
mass points.

Output: a theorem artifact stating that the present D12 mass side determines
only the emitted mass ray ``D12_ud_mass_ray`` with unresolved coordinate
``ray_modulus``.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCALARIZED_BUNDLE_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_scalarized_continuation_bundle.json"
ONE_SCALAR_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_d12_one_scalar_specialization.json"
D12_MASS_BRANCH_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_d12_mass_branch_and_ckm_residual.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "flavor" / "quark_d12_mass_side_underdetermination_theorem.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the D12 quark mass-side underdetermination theorem artifact.")
    parser.add_argument("--scalarized-bundle", default=str(SCALARIZED_BUNDLE_JSON))
    parser.add_argument("--one-scalar", default=str(ONE_SCALAR_JSON))
    parser.add_argument("--mass-branch", default=str(D12_MASS_BRANCH_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    scalarized_bundle = _load_json(Path(args.scalarized_bundle))
    one_scalar = _load_json(Path(args.one_scalar))
    mass_branch = _load_json(Path(args.mass_branch))

    sample_same_family_point = dict(one_scalar["sample_same_family_point"])
    specialization_formulas = dict(one_scalar["specialization_formulas"])
    sample_mass_point = dict(mass_branch["sample_same_family_point"])
    comparison_only_best_same_family_point = dict(mass_branch["comparison_only_best_same_family_point"])
    honest_remaining_value_laws = list(scalarized_bundle["honest_remaining_value_laws"])

    ray_modulus = float(sample_same_family_point["ray_modulus"])
    x2 = float(sample_same_family_point["x2"])
    delta_per_t1 = 1.0 / 5.0
    eta_per_t1 = -((1.0 - x2 * x2) / 27.0)
    ray_law_coefficient = -5.0 * (1.0 - x2 * x2) / 27.0

    artifact = {
        "artifact": "oph_quark_d12_mass_side_underdetermination_theorem",
        "generated_utc": _timestamp(),
        "scope": "D12_continuation_only",
        "proof_status": "same_family_mass_side_ray_closed_scale_fixing_law_open",
        "public_promotion_allowed": False,
        "theorem_statement": (
            "On the present same-family D12 continuation branch, the mass-side deformation "
            "is reduced to the one-parameter ray "
            "(Delta_ud_overlap, eta_Q_centered) = "
            "ray_modulus * (1/5, -((1 - x2^2) / 27)). "
            "Equivalently eta_Q_centered = -(5 * (1 - x2^2) / 27) * Delta_ud_overlap. "
            "The current OPH chain emits the ray but not a theorem-grade intrinsic scale-fixing law "
            "that would select one unique point on it."
        ),
        "same_family_ray": {
            "ray_name": "D12_ud_mass_ray",
            "ray_parameter": "ray_modulus",
            "ray_formulas": {
                "Delta_ud_overlap": "ray_modulus / 5",
                "eta_Q_centered": "-((1 - x2^2) / 27) * ray_modulus",
                "kappa_Q": "-ray_modulus / 54",
                "eta_Q_centered_from_Delta_ud_overlap": "-(5 * (1 - x2^2) / 27) * Delta_ud_overlap",
            },
            "ray_direction_values": {
                "delta_ud_overlap_per_ray_modulus": delta_per_t1,
                "eta_q_centered_per_ray_modulus": eta_per_t1,
                "eta_q_centered_per_delta_ud_overlap": ray_law_coefficient,
            },
            "ordered_family_coordinate_x2": x2,
        },
        "remaining_object": {
            "id": "D12_ud_mass_ray",
            "unresolved_coordinate": "ray_modulus",
            "ray_modulus_equals_t1": True,
        },
        "same_family_specialization_sample": {
            "formulas": specialization_formulas,
            "sample_same_family_point": sample_same_family_point,
        },
        "diagnostic_mass_points": {
            "sample_same_family_point": sample_mass_point,
            "comparison_only_best_same_family_point": comparison_only_best_same_family_point,
        },
        "no_go_theorem": {
            "id": "quark_d12_same_family_mass_side_scale_underdetermination",
            "conclusion": (
                "The present D12 mass-side branch determines only the one-parameter ray "
                "D12_ud_mass_ray and does not yet emit a theorem-grade intrinsic scale law "
                "that selects a unique ray_modulus."
            ),
            "forbidden_promotions": [
                "target_mass_backsolve_as_intrinsic_scale_law_D12",
                "compare_derived_exact_mean_specialization_as_OPH_emitted",
            ],
        },
        "honest_remaining_value_laws": honest_remaining_value_laws,
        "next_exact_missing_object": "D12_ud_mass_ray",
        "minimal_new_theorem": {
            "id": "intrinsic_scale_law_D12",
            "must_emit": "intrinsic_scale_law_D12",
            "unique_intersection_with": "D12_ud_mass_ray",
            "then_emits": ["ray_modulus", "Delta_ud_overlap", "eta_Q_centered"],
            "must_not_use_target_masses": True,
            "must_not_use_ckm_cp": True,
        },
        "notes": [
            "This artifact sharpens the current D12 mass-side status: the current branch emits the same-family mass ray, not a distinguished modulus on that ray.",
            "The retained numerical same-family point uses t1_sample = ray_modulus = 0.6695617711471163 and is sample-only, not theorem-grade emission.",
            "It does not by itself prove that the present D12 continuation branch is the physically correct quark branch.",
            "The physical-branch question remains separate from the mass-side no-go recorded here.",
        ],
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
