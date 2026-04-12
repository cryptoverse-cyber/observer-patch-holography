#!/usr/bin/env python3
"""Expose a direct edge-statistics candidate for the quark spread pair.

Chain role: make the strongest current local bridge from overlap-edge
statistics to the quark spread pair explicit instead of leaving it hidden as a
fallback inside the spread-map builder.

Mathematics: combine the shared charged suppression seed with the ordered
branch-generator gap ratio to produce one candidate pair
`(sigma_u_total_log_per_side, sigma_d_total_log_per_side)` on the realized
three-point family.

OPH-derived inputs: the overlap-edge cocycle suppressions, the ordered-family
spectral package, and the shared charged response seed already exported by the
odd-response law.

Output: a candidate-only bridge artifact that can be compared directly against
the active same-family spread pair without promoting the theorem boundary.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FAMILY = ROOT / "particles" / "runs" / "flavor" / "family_excitation_evaluator.json"
DEFAULT_ODD_RESPONSE = ROOT / "particles" / "runs" / "flavor" / "quark_odd_response_law.json"
DEFAULT_COCYCLE = ROOT / "particles" / "runs" / "flavor" / "overlap_edge_transport_cocycle.json"
DEFAULT_SPREAD = ROOT / "particles" / "runs" / "flavor" / "quark_spread_map.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "flavor" / "quark_edge_statistics_spread_candidate.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _relative_error(candidate: float, reference: float | None) -> float | None:
    if reference is None or abs(reference) <= 1.0e-12:
        return None
    return float((candidate - reference) / reference)


def _profile_rays(rho: float) -> tuple[list[float], list[float]]:
    denom = 3.0 * (1.0 + rho)
    v_u = [
        -((2.0 * rho) + 1.0) / denom,
        (rho - 1.0) / denom,
        (rho + 2.0) / denom,
    ]
    v_d = [
        -((rho + 2.0) / denom),
        (1.0 - rho) / denom,
        ((2.0 * rho) + 1.0) / denom,
    ]
    return v_u, v_d


def build_artifact(
    family_excitation: dict[str, Any],
    odd_response: dict[str, Any],
    cocycle: dict[str, Any],
    spread_map: dict[str, Any] | None,
) -> dict[str, Any]:
    rho = float(family_excitation["rho_ord"])
    x2 = float(family_excitation["family_coordinate_x"][1])
    delta21 = float(family_excitation["ordered_spectral_gaps"][0])
    mean_denominator = 1.0 + rho - x2 * x2

    s_ch = odd_response["shared_charged_response_seed"]["S_ch"]
    s13 = float(s_ch[0][2])
    s23 = float(s_ch[1][2])
    cocycle_s = cocycle["derived_pairwise_suppression"]
    cocycle_s13 = float(cocycle_s[0][2])
    cocycle_s23 = float(cocycle_s[1][2])

    sigma_u = s13 + (rho * delta21 / (1.0 + rho))
    sigma_d = s23 + (delta21 / (2.0 * mean_denominator))
    v_u, v_d = _profile_rays(rho)
    e_u = [sigma_u * value for value in v_u]
    e_d = [sigma_d * value for value in v_d]

    closed_sigma_u = None if spread_map is None else float(spread_map["sigma_u_total_log_per_side"])
    closed_sigma_d = None if spread_map is None else float(spread_map["sigma_d_total_log_per_side"])
    residual_u = None if closed_sigma_u is None else sigma_u - closed_sigma_u
    residual_d = None if closed_sigma_d is None else sigma_d - closed_sigma_d
    shared_seed_matches_cocycle = abs(s13 - cocycle_s13) <= 1.0e-12 and abs(s23 - cocycle_s23) <= 1.0e-12

    return {
        "artifact": "oph_quark_edge_statistics_spread_candidate",
        "generated_utc": _timestamp(),
        "bridge_status": "candidate_only",
        "candidate_kind": "shared_edge_suppression_plus_ordered_gap",
        "input_artifacts": {
            "family_excitation_evaluator": family_excitation.get("artifact"),
            "quark_odd_response_law": odd_response.get("artifact"),
            "overlap_edge_transport_cocycle": cocycle.get("artifact"),
            "comparison_spread_map": None if spread_map is None else spread_map.get("artifact"),
        },
        "ordered_family_inputs": {
            "rho_ord": rho,
            "delta21": delta21,
            "x2": x2,
            "mean_denominator": mean_denominator,
        },
        "edge_statistics_inputs": {
            "shared_charged_suppression_seed": {
                "S_13": s13,
                "S_23": s23,
            },
            "cocycle_pairwise_suppression": {
                "S_13": cocycle_s13,
                "S_23": cocycle_s23,
            },
            "shared_seed_matches_cocycle": shared_seed_matches_cocycle,
        },
        "candidate_formulas": {
            "sigma_u_total_log_per_side": "S_13 + rho_ord * delta21 / (1 + rho_ord)",
            "sigma_d_total_log_per_side": "S_23 + delta21 / (2 * (1 + rho_ord - x2^2))",
            "E_u_log": "sigma_u_total_log_per_side * v_u",
            "E_d_log": "sigma_d_total_log_per_side * v_d",
        },
        "profile_rays": {
            "v_u": v_u,
            "v_d": v_d,
        },
        "candidate_sigmas": {
            "sigma_u_total_log_per_side": sigma_u,
            "sigma_d_total_log_per_side": sigma_d,
        },
        "candidate_centered_even_logs": {
            "E_u_log": e_u,
            "E_d_log": e_d,
        },
        "comparison_to_active_spread_pair": {
            "status": None if spread_map is None else spread_map.get("spread_emitter_status"),
            "sigma_source_kind": None if spread_map is None else spread_map.get("sigma_source_kind"),
            "closed_sigma_u_total_log_per_side": closed_sigma_u,
            "closed_sigma_d_total_log_per_side": closed_sigma_d,
            "sigma_u_residual": residual_u,
            "sigma_d_residual": residual_d,
            "sigma_u_relative_error": _relative_error(sigma_u, closed_sigma_u),
            "sigma_d_relative_error": _relative_error(sigma_d, closed_sigma_d),
        },
        "notes": [
            "This artifact does not promote the Yukawa dictionary to theorem status.",
            "It exposes the strongest current direct bridge from edge-side suppression data to the quark spread pair on the realized ordered family.",
            "The candidate is intended as a constructive theorem target for the Yukawa-dictionary search rather than as a compare-only afterthought.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the quark edge-statistics spread candidate artifact.")
    parser.add_argument("--family", default=str(DEFAULT_FAMILY))
    parser.add_argument("--odd-response", default=str(DEFAULT_ODD_RESPONSE))
    parser.add_argument("--cocycle", default=str(DEFAULT_COCYCLE))
    parser.add_argument("--spread", default=str(DEFAULT_SPREAD))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    family_excitation = json.loads(Path(args.family).read_text(encoding="utf-8"))
    odd_response = json.loads(Path(args.odd_response).read_text(encoding="utf-8"))
    cocycle = json.loads(Path(args.cocycle).read_text(encoding="utf-8"))
    spread_path = Path(args.spread)
    spread_map = json.loads(spread_path.read_text(encoding="utf-8")) if spread_path.exists() else None
    artifact = build_artifact(family_excitation, odd_response, cocycle, spread_map)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
