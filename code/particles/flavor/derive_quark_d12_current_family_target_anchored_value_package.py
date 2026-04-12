#!/usr/bin/env python3
"""Emit a computed D12 scalar package on the exact current-family surface.

Chain role: compute the remaining D12 mass/source/transport scalar package from
the strongest exact current-family witness already on disk, without pretending
that this target-anchored computation is a public theorem.

Mathematics: use the exact current-family light masses to compute
ell_ud = log(m_d / m_u), then apply the standing D12 normalization route
Delta_ud_overlap = ell_ud / 6 and t1 = 5 * Delta_ud_overlap, together with the
already-closed theorem-grade sigma branch and exact transport reduction.

Output: one current-family-only sidecar that exposes the numerically computed
missing scalar package explicitly for proof comparison and worker guidance.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
EXACT_READOUT_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_exact_readout.json"
LIGHT_RATIO_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_light_ratio_theorem.json"
SPREAD_MAP_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_spread_map.json"
OVERLAP_LAW_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_d12_overlap_transport_law.json"
MASS_RAY_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_d12_mass_ray.json"
INTERNAL_BACKREAD_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_d12_internal_backread_continuation_closure.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "flavor" / "quark_d12_current_family_target_anchored_value_package.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload(
    exact_readout: dict[str, Any],
    light_ratio_theorem: dict[str, Any] | None,
    spread_map: dict[str, Any],
    overlap_law: dict[str, Any],
    mass_ray: dict[str, Any],
    internal_backread: dict[str, Any] | None = None,
) -> dict[str, Any]:
    m_u = float(exact_readout["predicted_singular_values_u"][0])
    m_d = float(exact_readout["predicted_singular_values_d"][0])
    ell_ud = (
        float(light_ratio_theorem["exact_light_data"]["ell_ud"])
        if light_ratio_theorem is not None
        else math.log(m_d / m_u)
    )
    delta_ud_overlap = ell_ud / 6.0
    t1 = 5.0 * delta_ud_overlap
    x2 = float(mass_ray["sample_same_family_point"]["x2"])
    sigma_u = float(spread_map["sigma_u_total_log_per_side"])
    sigma_d = float(spread_map["sigma_d_total_log_per_side"])
    tau_u = sigma_d * delta_ud_overlap / (2.0 * (sigma_u + sigma_d))
    tau_d = sigma_u * delta_ud_overlap / (2.0 * (sigma_u + sigma_d))
    lambda_ud_b = sigma_u * sigma_d * delta_ud_overlap / (2.0 * (sigma_u + sigma_d))
    sample_point = dict(mass_ray["sample_same_family_point"])
    comparison = {
        "sample_same_family_point": {
            "Delta_ud_overlap": float(sample_point["Delta_ud_overlap"]),
            "t1": float(sample_point["t1_sample"]),
            "eta_Q_centered": float(sample_point["eta_Q_centered"]),
        },
        "difference_vs_sample_same_family_point": {
            "Delta_ud_overlap": delta_ud_overlap - float(sample_point["Delta_ud_overlap"]),
            "t1": t1 - float(sample_point["t1_sample"]),
            "eta_Q_centered": (-((1.0 - x2 * x2) / 27.0) * t1) - float(sample_point["eta_Q_centered"]),
        },
    }
    if internal_backread is not None:
        backread_mass = dict(internal_backread["closed_mass_side_package"])
        comparison["internal_backread"] = {
            "Delta_ud_overlap": float(backread_mass["Delta_ud_overlap"]),
            "t1": float(backread_mass["t1"]),
            "eta_Q_centered": float(backread_mass["eta_Q_centered"]),
        }
        comparison["difference_vs_internal_backread"] = {
            "Delta_ud_overlap": delta_ud_overlap - float(backread_mass["Delta_ud_overlap"]),
            "t1": t1 - float(backread_mass["t1"]),
            "eta_Q_centered": (-((1.0 - x2 * x2) / 27.0) * t1) - float(backread_mass["eta_Q_centered"]),
        }
    return {
        "artifact": "oph_quark_d12_current_family_target_anchored_value_package",
        "generated_utc": _timestamp(),
        "scope": "current_family_only",
        "proof_status": "computed_target_anchored_value_package_from_exact_current_family_witness",
        "public_promotion_allowed": False,
        "theorem_boundary_note": (
            "This sidecar computes the missing D12 scalar package from the exact current-family witness. "
            "It is not a public theorem-grade emission of light_quark_overlap_defect_value_law or quark_d12_t1_value_law."
        ),
        "source_artifacts": {
            "exact_readout": exact_readout["artifact"],
            "light_ratio_theorem": None if light_ratio_theorem is None else light_ratio_theorem["artifact"],
            "spread_map": spread_map["artifact"],
            "overlap_transport_law": overlap_law["artifact"],
            "mass_ray": mass_ray["artifact"],
        },
        "target_anchored_inputs": {
            "m_u": m_u,
            "m_d": m_d,
            "light_mass_ratio": m_d / m_u,
            "ell_ud_formula": "log(m_d / m_u)",
            "ell_ud": ell_ud,
        },
        "computed_d12_scalars": {
            "Delta_ud_overlap_formula": "(1/6) * ell_ud",
            "Delta_ud_overlap": delta_ud_overlap,
            "t1_formula": "(5/6) * ell_ud",
            "t1": t1,
            "ray_modulus": t1,
            "eta_Q_centered_formula": "-((1 - x2^2) / 27) * t1",
            "eta_Q_centered": -((1.0 - x2 * x2) / 27.0) * t1,
            "kappa_Q_formula": "-t1 / 54",
            "kappa_Q": -t1 / 54.0,
        },
        "forced_source_payload": {
            "beta_u_diag_B_source_formula": "t1 / 10",
            "beta_u_diag_B_source": t1 / 10.0,
            "beta_d_diag_B_source_formula": "-t1 / 10",
            "beta_d_diag_B_source": -t1 / 10.0,
            "source_readback_u_log_per_side": [-t1 / 10.0, 0.0, t1 / 10.0],
            "source_readback_d_log_per_side": [t1 / 10.0, 0.0, -t1 / 10.0],
        },
        "transport_on_theorem_grade_sigma_branch": {
            "sigma_source_kind": spread_map["sigma_source_kind"],
            "sigma_u_total_log_per_side": sigma_u,
            "sigma_d_total_log_per_side": sigma_d,
            "tau_u_log_per_side_formula": overlap_law["exact_transport_contract"]["given_any_fixed_sigma_branch"]["tau_u_log_per_side"],
            "tau_u_log_per_side": tau_u,
            "tau_d_log_per_side_formula": overlap_law["exact_transport_contract"]["given_any_fixed_sigma_branch"]["tau_d_log_per_side"],
            "tau_d_log_per_side": tau_d,
            "Lambda_ud_B_transport_formula": overlap_law["exact_transport_contract"]["given_any_fixed_sigma_branch"]["Lambda_ud_B_transport"],
            "Lambda_ud_B_transport": lambda_ud_b,
            "tau_u_plus_tau_d": tau_u + tau_d,
            "tau_d_over_tau_u": tau_d / tau_u,
        },
        "comparison_to_other_local_d12_packages": comparison,
        "equivalent_public_target_if_promotable": {
            "light_quark_overlap_defect_value_law": {
                "Delta_ud_overlap": delta_ud_overlap,
            },
            "quark_d12_t1_value_law": {
                "t1": t1,
                "ray_modulus": t1,
            },
        },
        "computed_candidate_theorem_texts": {
            "light_quark_overlap_defect_value_law": (
                "On the exact current-family light-quark witness, "
                "Delta_ud_overlap = (1/6) * log(m_d / m_u)."
            ),
            "quark_d12_t1_value_law": (
                "On the exact current-family light-quark witness, "
                "t1 = ray_modulus = (5/6) * log(m_d / m_u), equivalently "
                "Delta_ud_overlap = t1 / 5."
            ),
        },
        "computed_candidate_theorem_values": {
            "light_quark_overlap_defect_value_law": {
                "Delta_ud_overlap": delta_ud_overlap,
            },
            "quark_d12_t1_value_law": {
                "ell_ud": ell_ud,
                "t1": t1,
                "ray_modulus": t1,
                "Delta_ud_overlap": delta_ud_overlap,
                "eta_Q_centered": -((1.0 - x2 * x2) / 27.0) * t1,
                "kappa_Q": -t1 / 54.0,
            },
        },
        "notes": [
            "The input masses are taken from the exact current-family readout witness, which is target-anchored and explicitly not public-promotion-allowed.",
            "This package is useful for local theorem search and consistency checks because it computes the exact missing scalar package the public proof is trying to internalize.",
            "Numerically, this target-anchored current-family package differs from the existing continuation-only internal-backread values, so it should not be conflated with the public theorem frontier.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the current-family target-anchored D12 value package.")
    parser.add_argument("--exact-readout", default=str(EXACT_READOUT_JSON))
    parser.add_argument("--light-ratio-theorem", default=str(LIGHT_RATIO_JSON))
    parser.add_argument("--spread-map", default=str(SPREAD_MAP_JSON))
    parser.add_argument("--overlap-law", default=str(OVERLAP_LAW_JSON))
    parser.add_argument("--mass-ray", default=str(MASS_RAY_JSON))
    parser.add_argument("--internal-backread", default=str(INTERNAL_BACKREAD_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    internal_backread_path = Path(args.internal_backread)
    light_ratio_path = Path(args.light_ratio_theorem)
    payload = build_payload(
        _load_json(Path(args.exact_readout)),
        _load_json(light_ratio_path) if light_ratio_path.exists() else None,
        _load_json(Path(args.spread_map)),
        _load_json(Path(args.overlap_law)),
        _load_json(Path(args.mass_ray)),
        _load_json(internal_backread_path) if internal_backread_path.exists() else None,
    )
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
