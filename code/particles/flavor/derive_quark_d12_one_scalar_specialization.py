#!/usr/bin/env python3
"""Package the diagnostic one-ray-modulus D12 quark specialization.

Chain role: make the strongest current same-family D12 specialization explicit
without promoting it as an OPH-derived value law.

Mathematics: combine the odd overlap-transport law and the scalarized even
transport shell under the shared diagnostic ray coordinate `ray_modulus`,
where `Delta_ud_overlap = ray_modulus / 5` and
`eta_Q_centered = -((1 - x2^2) / 27) * ray_modulus`.

OPH-derived inputs: the D12 overlap transport law, the scalarized quadratic-even
shell, and the current D12 mass-branch diagnostic.

Output: one diagnostic artifact that reduces the D12 same-family mass-side
specialization to one unresolved ray coordinate on the sample branch, without
promoting that sample to an OPH-emitted value law.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OVERLAP_LAW = ROOT / "particles" / "runs" / "flavor" / "quark_d12_overlap_transport_law.json"
DEFAULT_QUADRATIC_SCALAR = ROOT / "particles" / "runs" / "flavor" / "quark_quadratic_even_transport_scalar.json"
DEFAULT_MASS_BRANCH = ROOT / "particles" / "runs" / "flavor" / "quark_d12_mass_branch_and_ckm_residual.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "flavor" / "quark_d12_one_scalar_specialization.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the diagnostic one-scalar D12 quark specialization artifact.")
    parser.add_argument("--overlap-law", default=str(DEFAULT_OVERLAP_LAW))
    parser.add_argument("--quadratic-scalar", default=str(DEFAULT_QUADRATIC_SCALAR))
    parser.add_argument("--mass-branch", default=str(DEFAULT_MASS_BRANCH))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    overlap_law = _load_json(Path(args.overlap_law))
    quadratic_scalar = _load_json(Path(args.quadratic_scalar))
    mass_branch = _load_json(Path(args.mass_branch))

    sample_ray_point = dict(quadratic_scalar["sample_same_family_ray_point"])
    t1_sample = float(sample_ray_point["t1_sample"])
    x2 = float(quadratic_scalar["x2"])
    delta = float(t1_sample / 5.0)
    eta_q = float(-((1.0 - x2 * x2) / 27.0) * t1_sample)
    kappa_q = float(-t1_sample / 54.0)
    overlap_sample = dict(overlap_law["sample_same_family_point"])
    mass_sample = dict(mass_branch["sample_same_family_point"])

    artifact = {
        "artifact": "oph_quark_d12_one_scalar_specialization",
        "generated_utc": _timestamp(),
        "scope": "D12_continuation_only",
        "proof_status": "diagnostic_same_family_ray_specialization_not_OPH_derived",
        "public_promotion_allowed": False,
        "scalar_name": "ray_modulus",
        "sample_scalar_name": "t1_sample",
        "next_single_residual_object": "D12_ud_mass_ray",
        "mass_side_object_count_reduction": {
            "broader_mass_side_value_laws": ["Delta_ud_overlap_value_law", "eta_Q_centered_value_law"],
            "same_family_diagnostic_specialization": ["D12_ud_mass_ray"],
        },
        "specialization_formulas": {
            "Delta_ud_overlap": "ray_modulus / 5",
            "eta_Q_centered": "-((1 - x2^2) / 27) * ray_modulus",
            "kappa_Q": "-ray_modulus / 54",
            "tau_u_log_per_side": overlap_law["transport_formulas"]["tau_u_log_per_side"].replace("Delta_ud_overlap", "(ray_modulus / 5)"),
            "tau_d_log_per_side": overlap_law["transport_formulas"]["tau_d_log_per_side"].replace("Delta_ud_overlap", "(ray_modulus / 5)"),
            "Lambda_ud_B_transport": overlap_law["transport_formulas"]["Lambda_ud_B_transport"].replace("Delta_ud_overlap", "(ray_modulus / 5)"),
            "quadratic_even_log_formula_direct": quadratic_scalar["quadratic_even_log_formula_direct"].replace("eta_Q_centered", "(-((1 - x2^2) / 27) * ray_modulus)"),
        },
        "sample_same_family_point": {
            "ray_modulus": t1_sample,
            "t1_sample": t1_sample,
            "x2": x2,
            "Delta_ud_overlap": delta,
            "eta_Q_centered": eta_q,
            "kappa_Q": kappa_q,
            "tau_u_log_per_side": overlap_sample["tau_u_log_per_side"],
            "tau_d_log_per_side": overlap_sample["tau_d_log_per_side"],
            "Lambda_ud_B_transport": overlap_sample["Lambda_ud_B_transport"],
        },
        "sample_same_family_mass_point": {
            "m_u_GeV": mass_sample["m_u"],
            "m_d_GeV": mass_sample["m_d"],
            "rms_log_error_vs_reference_targets": mass_sample["rms_log_error_vs_reference_targets"],
        },
        "consistency_checks": {
            "delta_matches_overlap_sample": abs(delta - float(overlap_sample["Delta_ud_overlap"])) <= 1.0e-15,
            "eta_matches_quadratic_sample": abs(eta_q - float(sample_ray_point["eta_Q_centered"])) <= 1.0e-15,
            "kappa_matches_quadratic_sample": abs(kappa_q - float(sample_ray_point["kappa_Q"])) <= 1.0e-15,
            "transport_identity_tau_sum_half_delta": abs(float(overlap_sample["tau_sum_half_delta_identity"])) <= 1.0e-15,
            "transport_identity_tau_ratio": abs(float(overlap_sample["tau_ratio_minus_sigma_ratio"])) <= 1.0e-12,
        },
        "notes": [
            "This artifact does not claim that the D12 branch already emits a theorem-grade ray modulus.",
            "It records that the strongest same-family D12 diagnostic specialization collapses both mass-side continuation scalars to one ray coordinate on the emitted same-family mass ray.",
            "The retained numerical point is sample-only and is labeled by t1_sample = ray_modulus = 0.6695617711471163.",
            "On this branch CKM/CP closes once the forward Yukawas are emitted; the remaining open burden is the intrinsic scale law that would select a unique point on the D12_ud_mass_ray.",
        ],
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
