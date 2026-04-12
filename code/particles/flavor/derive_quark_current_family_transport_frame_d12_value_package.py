#!/usr/bin/env python3
"""Emit the exact D12 scalar package on the restricted transport-frame carrier."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LIGHT_RATIO_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_transport_frame_light_ratio_theorem.json"
SPREAD_MAP_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_spread_map.json"
OVERLAP_LAW_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_d12_overlap_transport_law.json"
MASS_RAY_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_d12_mass_ray.json"
DEFAULT_OUT = (
    ROOT / "particles" / "runs" / "flavor" / "quark_current_family_transport_frame_d12_value_package.json"
)


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_artifact(light_ratio: dict, spread_map: dict, overlap_law: dict, mass_ray: dict) -> dict:
    ell_ud = float(light_ratio["exact_light_data"]["ell_ud"])
    delta_ud_overlap = ell_ud / 6.0
    t1 = 5.0 * delta_ud_overlap
    x2 = float(mass_ray["sample_same_family_point"]["x2"])
    sigma_u = float(spread_map["sigma_u_total_log_per_side"])
    sigma_d = float(spread_map["sigma_d_total_log_per_side"])
    tau_u = sigma_d * delta_ud_overlap / (2.0 * (sigma_u + sigma_d))
    tau_d = sigma_u * delta_ud_overlap / (2.0 * (sigma_u + sigma_d))
    lambda_ud_b = sigma_u * sigma_d * delta_ud_overlap / (2.0 * (sigma_u + sigma_d))
    return {
        "artifact": "oph_quark_current_family_transport_frame_d12_value_package",
        "generated_utc": _timestamp(),
        "proof_status": "closed_current_family_transport_frame_d12_value_package",
        "theorem_scope": light_ratio["theorem_scope"],
        "public_promotion_allowed": False,
        "supporting_artifacts": {
            "light_ratio_theorem": light_ratio["artifact"],
            "spread_map": spread_map["artifact"],
            "overlap_transport_law": overlap_law["artifact"],
            "mass_ray": mass_ray["artifact"],
        },
        "theorem_statement": (
            "On the explicit current-family common-refinement transport-frame carrier, the exact light-ratio scalar "
            "ell_ud fixes the D12 mass/source/transport scalar package by Delta_ud_overlap = ell_ud / 6 and "
            "t1 = 5 * Delta_ud_overlap."
        ),
        "exact_transport_frame_light_ratio": {
            "ell_ud": ell_ud,
            "ell_ud_formula": "log(m_d / m_u)",
        },
        "closed_d12_scalars": {
            "Delta_ud_overlap": delta_ud_overlap,
            "Delta_ud_overlap_formula": "(1/6) * ell_ud",
            "t1": t1,
            "t1_formula": "(5/6) * ell_ud",
            "ray_modulus": t1,
            "eta_Q_centered": -((1.0 - x2 * x2) / 27.0) * t1,
            "eta_Q_centered_formula": "-((1 - x2^2) / 27) * t1",
            "kappa_Q": -t1 / 54.0,
            "kappa_Q_formula": "-t1 / 54",
        },
        "forced_source_payload": {
            "beta_u_diag_B_source": t1 / 10.0,
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
        },
        "notes": [
            "This is the restricted-carrier numeric D12 package above the exact transport-frame PDG completion surface.",
            "It is stronger than the older selected-sheet target-anchored D12 sidecar because it lives on the declared common-refinement transport-frame theorem surface.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the restricted-carrier quark D12 value package artifact.")
    parser.add_argument("--light-ratio", default=str(LIGHT_RATIO_JSON))
    parser.add_argument("--spread-map", default=str(SPREAD_MAP_JSON))
    parser.add_argument("--overlap-law", default=str(OVERLAP_LAW_JSON))
    parser.add_argument("--mass-ray", default=str(MASS_RAY_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    payload = build_artifact(
        _load_json(Path(args.light_ratio)),
        _load_json(Path(args.spread_map)),
        _load_json(Path(args.overlap_law)),
        _load_json(Path(args.mass_ray)),
    )
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
