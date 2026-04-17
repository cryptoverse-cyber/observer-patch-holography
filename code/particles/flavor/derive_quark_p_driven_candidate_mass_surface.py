#!/usr/bin/env python3
"""Emit a P-driven candidate quark mass surface anchored at the exact default universe.

Chain role: turn the candidate spread map into moving quark masses without
pretending the full off-canonical theorem frontier is already closed.

Mathematics: keep the exact selected-class current-family masses fixed at the
default-universe anchor, then transport away from that point by the candidate
sector-mean and candidate centered even-log shifts implied by the current
spread package.

OPH-derived inputs: the candidate spread map, the canonical current-surface
spread geometry, and the exact current-family readout.

Output: a compare-and-runtime-friendly quark mass surface that is exact at the
default-universe setting and moves coherently with ``P`` off that point.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from p_driven_flavor_candidate import sigma_to_even_logs, sigma_to_sector_means


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SPREAD = ROOT / "particles" / "runs" / "flavor" / "quark_spread_map.json"
DEFAULT_BASELINE_SPREAD = ROOT / "particles" / "runs" / "flavor" / "quark_spread_map.json"
DEFAULT_EXACT_READOUT = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_exact_readout.json"
DEFAULT_EXACT_SIGMA_TARGET = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_exact_sigma_target.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "flavor" / "quark_p_driven_candidate_mass_surface.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log(value: float) -> float:
    if value <= 0.0:
        raise ValueError("log requested on non-positive mass datum")
    return math.log(value)


def _build_sector_package(
    *,
    rho_ord: float,
    x2: float,
    g_ch: float,
    sigma_u: float,
    sigma_d: float,
) -> dict[str, Any]:
    means = sigma_to_sector_means(rho_ord, x2, g_ch, sigma_u, sigma_d)
    logs = sigma_to_even_logs(rho_ord, sigma_u, sigma_d)
    return {
        **means,
        **logs,
    }


def build_artifact(
    spread_map: dict[str, Any],
    baseline_spread_map: dict[str, Any],
    exact_readout: dict[str, Any],
    exact_sigma_target: dict[str, Any],
) -> dict[str, Any]:
    shared_norm_value = spread_map.get("shared_norm_value", baseline_spread_map.get("shared_norm_value"))
    if shared_norm_value is None:
        raise ValueError("spread maps must expose shared_norm_value for the anchored mass surface")
    g_ch = float(shared_norm_value)

    baseline_target = dict(exact_sigma_target["unique_exact_sigma_target"])
    baseline_package = _build_sector_package(
        rho_ord=float(baseline_spread_map["rho_ord"]),
        x2=float(baseline_spread_map["normalized_coordinate_x2"]),
        g_ch=g_ch,
        sigma_u=float(baseline_target["sigma_u_target"]),
        sigma_d=float(baseline_target["sigma_d_target"]),
    )
    current_package = _build_sector_package(
        rho_ord=float(spread_map["rho_ord"]),
        x2=float(spread_map["normalized_coordinate_x2"]),
        g_ch=g_ch,
        sigma_u=float(spread_map["sigma_u_total_log_per_side"]),
        sigma_d=float(spread_map["sigma_d_total_log_per_side"]),
    )

    exact_u = [float(value) for value in exact_readout["predicted_singular_values_u"]]
    exact_d = [float(value) for value in exact_readout["predicted_singular_values_d"]]
    labels_u = ["up", "charm", "top"]
    labels_d = ["down", "strange", "bottom"]

    # The remaining math debt is the off-canonical odd/pure-B lane. For now the
    # candidate surface moves by the sector means and the centered even logs only.
    delta_log_g_u = current_package["log_shift_u"] - baseline_package["log_shift_u"]
    delta_log_g_d = current_package["log_shift_d"] - baseline_package["log_shift_d"]
    candidate_u = [
        exact_u[idx] * math.exp(delta_log_g_u + current_package["E_u_log"][idx] - baseline_package["E_u_log"][idx])
        for idx in range(3)
    ]
    candidate_d = [
        exact_d[idx] * math.exp(delta_log_g_d + current_package["E_d_log"][idx] - baseline_package["E_d_log"][idx])
        for idx in range(3)
    ]

    return {
        "artifact": "oph_quark_p_driven_candidate_mass_surface",
        "generated_utc": _timestamp(),
        "proof_status": "candidate_only",
        "candidate_kind": "default_universe_exact_anchor_plus_p_driven_sigma_motion",
        "public_promotion_allowed": False,
        "input_artifacts": {
            "spread_map": spread_map.get("artifact"),
            "baseline_spread_map": baseline_spread_map.get("artifact"),
            "exact_readout": exact_readout.get("artifact"),
            "exact_sigma_target": exact_sigma_target.get("artifact"),
        },
        "baseline_anchor": {
            "shared_norm_value": g_ch,
            "sigma_u_target": float(baseline_target["sigma_u_target"]),
            "sigma_d_target": float(baseline_target["sigma_d_target"]),
            "exact_u_masses": exact_u,
            "exact_d_masses": exact_d,
            "baseline_log_shift_u": baseline_package["log_shift_u"],
            "baseline_log_shift_d": baseline_package["log_shift_d"],
            "baseline_E_u_log": baseline_package["E_u_log"],
            "baseline_E_d_log": baseline_package["E_d_log"],
        },
        "current_candidate_surface": {
            "spread_emitter_status": spread_map.get("spread_emitter_status"),
            "sigma_source_kind": spread_map.get("sigma_source_kind"),
            "rho_ord": float(spread_map["rho_ord"]),
            "x2": float(spread_map["normalized_coordinate_x2"]),
            "sigma_u_total_log_per_side": float(spread_map["sigma_u_total_log_per_side"]),
            "sigma_d_total_log_per_side": float(spread_map["sigma_d_total_log_per_side"]),
            "current_log_shift_u": current_package["log_shift_u"],
            "current_log_shift_d": current_package["log_shift_d"],
            "current_E_u_log": current_package["E_u_log"],
            "current_E_d_log": current_package["E_d_log"],
        },
        "current_candidate_masses": {
            "up_sector": [
                {"label": label, "mass": value}
                for label, value in zip(labels_u, candidate_u, strict=True)
            ],
            "down_sector": [
                {"label": label, "mass": value}
                for label, value in zip(labels_d, candidate_d, strict=True)
            ],
        },
        "transport_formulas": {
            "delta_log_m_u_i": "delta_log_g_u + (E_u_log_i(P) - E_u_log_i(P_default))",
            "delta_log_m_d_i": "delta_log_g_d + (E_d_log_i(P) - E_d_log_i(P_default))",
            "m_u_i(P)": "m_u_i_exact(default) * exp(delta_log_m_u_i)",
            "m_d_i(P)": "m_d_i_exact(default) * exp(delta_log_m_d_i)",
        },
        "consistency_checks": {
            "default_u_anchor_recovery": [
                math.isclose(candidate_u[idx], exact_u[idx], rel_tol=0.0, abs_tol=1.0e-12)
                if math.isclose(float(spread_map["sigma_u_total_log_per_side"]), float(baseline_target["sigma_u_target"]), rel_tol=0.0, abs_tol=1.0e-12)
                and math.isclose(float(spread_map["sigma_d_total_log_per_side"]), float(baseline_target["sigma_d_target"]), rel_tol=0.0, abs_tol=1.0e-12)
                else None
                for idx in range(3)
            ],
            "default_d_anchor_recovery": [
                math.isclose(candidate_d[idx], exact_d[idx], rel_tol=0.0, abs_tol=1.0e-12)
                if math.isclose(float(spread_map["sigma_u_total_log_per_side"]), float(baseline_target["sigma_u_target"]), rel_tol=0.0, abs_tol=1.0e-12)
                and math.isclose(float(spread_map["sigma_d_total_log_per_side"]), float(baseline_target["sigma_d_target"]), rel_tol=0.0, abs_tol=1.0e-12)
                else None
                for idx in range(3)
            ],
            "log_mass_shifts_u": [
                delta_log_g_u + current_package["E_u_log"][idx] - baseline_package["E_u_log"][idx]
                for idx in range(3)
            ],
            "log_mass_shifts_d": [
                delta_log_g_d + current_package["E_d_log"][idx] - baseline_package["E_d_log"][idx]
                for idx in range(3)
            ],
        },
        "notes": [
            "This is the runtime/off-canonical quark mass surface candidate, not a theorem-grade arbitrary-P quark closure.",
            "The default-universe point is forced to the exact selected-class readout by construction.",
            "The remaining refinement is the off-canonical odd/pure-B lane; until that closes, the moving surface uses the sector means plus the centered even-log package only.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the anchored P-driven candidate quark mass surface.")
    parser.add_argument("--spread-map", default=str(DEFAULT_SPREAD))
    parser.add_argument("--baseline-spread-map", default=str(DEFAULT_BASELINE_SPREAD))
    parser.add_argument("--exact-readout", default=str(DEFAULT_EXACT_READOUT))
    parser.add_argument("--exact-sigma-target", default=str(DEFAULT_EXACT_SIGMA_TARGET))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    artifact = build_artifact(
        json.loads(Path(args.spread_map).read_text(encoding="utf-8")),
        json.loads(Path(args.baseline_spread_map).read_text(encoding="utf-8")),
        json.loads(Path(args.exact_readout).read_text(encoding="utf-8")),
        json.loads(Path(args.exact_sigma_target).read_text(encoding="utf-8")),
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
