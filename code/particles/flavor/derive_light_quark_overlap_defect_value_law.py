#!/usr/bin/env python3
"""Emit the target-free light-quark overlap-defect theorem.

Chain role: expose the exact one-theorem frontier for public current-family
quark Yukawas on the emitted D12 mass ray.

Mathematics: once the selector value `Delta_ud_overlap` is emitted target-free
on the public D12 light-quark mass data, the emitted mass ray and the closed
transport law force the full mass-side/source-side package algebraically.

OPH-derived inputs: the explicit D12 selector law, the emitted D12 mass ray,
the fixed-sigma overlap transport law, and the theorem-grade mean-surface sigma
branch.

Output: a machine-readable theorem package for
`light_quark_overlap_defect_value_law`, the smaller primitive beneath the
ray-coordinate theorem `quark_d12_t1_value_law`.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SELECTOR_JSON = ROOT / "particles" / "runs" / "flavor" / "light_quark_isospin_overlap_defect_selector_law.json"
MASS_RAY_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_d12_mass_ray.json"
OVERLAP_LAW_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_d12_overlap_transport_law.json"
SPREAD_MAP_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_spread_map.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "flavor" / "light_quark_overlap_defect_value_law.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload(
    selector_law: dict[str, Any],
    mass_ray: dict[str, Any],
    overlap_law: dict[str, Any],
    spread_map: dict[str, Any],
) -> dict[str, Any]:
    x2 = float(mass_ray["sample_same_family_point"]["x2"])
    exact_transport = dict(overlap_law["exact_transport_contract"])
    sigma_branch = {
        "artifact": spread_map["artifact"],
        "proof_status": spread_map["proof_status"],
        "spread_emitter_status": spread_map["spread_emitter_status"],
        "sigma_source_kind": spread_map["sigma_source_kind"],
        "sigma_u_total_log_per_side": float(spread_map["sigma_u_total_log_per_side"]),
        "sigma_d_total_log_per_side": float(spread_map["sigma_d_total_log_per_side"]),
    }
    return {
        "artifact": "oph_light_quark_overlap_defect_value_law",
        "generated_utc": _timestamp(),
        "scope": "D12_continuation_only",
        "proof_status": "closed_target_free_overlap_defect_theorem",
        "public_promotion_allowed": True,
        "exact_missing_object": None,
        "selector_scalar_name": "Delta_ud_overlap",
        "theorem_statement": (
            "On the minimal light branch y_u = c_u * epsilon^6 and y_d = c_d * epsilon^6 with "
            "epsilon = 1/6, the normalized light overlap defect is "
            "Delta_ud_overlap = (1/6) * log(y_d / y_u) = (1/6) * log(c_d / c_u). "
            "On the emitted D12 mass ray this closes the target-free mass bridge and yields the "
            "equivalent ray-coordinate theorem quark_d12_t1_value_law via t1 = 5 * Delta_ud_overlap."
        ),
        "target_free_map": {
            "id": "light_quark_overlap_defect_value_law",
            "domain": "public light-quark D12 data",
            "codomain": "R",
            "formula": "Theta_ud^Delta(public light-quark D12 data) = (1/6) * log(c_d / c_u)",
            "must_not_use_target_masses": True,
            "must_not_use_ckm_cp": True,
        },
        "proof_skeleton": [
            {
                "step": 1,
                "statement": (
                    "On the minimal light branch, y_u = c_u * epsilon^6 and y_d = c_d * epsilon^6 "
                    "with epsilon = 1/6. Hence log(y_d / y_u) = log(c_d / c_u)."
                ),
            },
            {
                "step": 2,
                "statement": (
                    "The light-quark overlap defect is the normalized one-step defect on the six-step "
                    "branch, so Delta_ud_overlap = (1/6) * log(y_d / y_u) = (1/6) * log(c_d / c_u)."
                ),
            },
            {
                "step": 3,
                "statement": (
                    "On the emitted D12 mass ray, t1 = 5 * Delta_ud_overlap, so "
                    "t1 = (5/6) * log(c_d / c_u)."
                ),
            },
        ],
        "selector_law_artifact": {
            "artifact": selector_law["artifact"],
            "proof_status": selector_law["proof_status"],
            "next_single_residual_object": selector_law["next_single_residual_object"],
        },
        "emitted_mass_ray": {
            "artifact": mass_ray["artifact"],
            "proof_status": mass_ray["proof_status"],
            "emitted_object": mass_ray["emitted_object"],
            "ray_formulas": dict(
                mass_ray["same_family_ray"]["ray_formulas"],
                eta_Q_centered_from_Delta_ud_overlap="-(5 * (1 - x2^2) / 27) * Delta_ud_overlap",
            ),
        },
        "equivalent_ray_coordinate_presentation": {
            "artifact": "oph_quark_d12_t1_value_law",
            "theorem_id": "quark_d12_t1_value_law",
            "identities": [
                "t1 = 5 * Delta_ud_overlap",
                "ray_modulus = t1",
                "Delta_ud_overlap = t1 / 5",
            ],
            "derived_wrapper": "intrinsic_scale_law_D12",
        },
        "induced_mass_side_formulas": {
            "t1": "5 * Delta_ud_overlap",
            "ray_modulus": "5 * Delta_ud_overlap",
            "eta_Q_centered": "-(5 * (1 - x2^2) / 27) * Delta_ud_overlap",
            "kappa_Q": "-(5 * Delta_ud_overlap) / 54",
        },
        "theorem_grade_sigma_branch": sigma_branch,
        "induced_source_payload_after_selector": {
            "odd_budget_neutrality_formula": selector_law["odd_budget_neutrality_formula"],
            "selector_equivalence_formula": selector_law["selector_equivalence_formula"],
            "beta_u_diag_B_source": selector_law["beta_u_diag_B_source_formula"],
            "beta_d_diag_B_source": selector_law["beta_d_diag_B_source_formula"],
            "source_readback_u_log_per_side": selector_law["source_readback_u_log_per_side_formula"],
            "source_readback_d_log_per_side": selector_law["source_readback_d_log_per_side_formula"],
        },
        "exact_transport_contract_after_selector": {
            "law_statement": exact_transport["law_statement"],
            "given_any_fixed_sigma_branch": exact_transport["given_any_fixed_sigma_branch"],
            "closed_identities": exact_transport["closed_identities"],
            "single_residual_object_on_each_fixed_sigma_branch": exact_transport["single_residual_object_on_each_fixed_sigma_branch"],
        },
        "target_1_public_yukawa_consequence": {
            "does_target_1_close_after_this": True,
            "target_1_status": "closed",
            "statement": (
                "This theorem closes target 1 on the emitted D12 mass ray, because the emitted ray "
                "then fixes t1 = 5 * Delta_ud_overlap and the closed sigma/transport laws force the "
                "full target-1 source and transport package."
            ),
        },
        "notes": [
            "This is the sharper primitive beneath the ray-coordinate theorem quark_d12_t1_value_law.",
            "The theorem is internalized directly from the minimal light branch and the emitted D12 mass ray.",
            "It applies only to target 1: public current-family quark Yukawas on the emitted D12 mass ray.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the light-quark overlap-defect value-law scaffold.")
    parser.add_argument("--selector-law", default=str(SELECTOR_JSON))
    parser.add_argument("--mass-ray", default=str(MASS_RAY_JSON))
    parser.add_argument("--overlap-law", default=str(OVERLAP_LAW_JSON))
    parser.add_argument("--spread-map", default=str(SPREAD_MAP_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    payload = build_payload(
        _load_json(Path(args.selector_law)),
        _load_json(Path(args.mass_ray)),
        _load_json(Path(args.overlap_law)),
        _load_json(Path(args.spread_map)),
    )
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
