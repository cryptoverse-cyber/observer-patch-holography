#!/usr/bin/env python3
"""Emit the exact sigma target implied by the current-family quark readout."""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXACT_READOUT_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_exact_readout.json"
SHARED_NORM_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_shared_absolute_norm_binding.json"
MEAN_SPLIT_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_sector_mean_split.json"
SPREAD_MAP_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_spread_map.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_exact_sigma_target.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_artifact(
    exact_readout: dict,
    shared_norm: dict,
    mean_split: dict,
    spread_map: dict,
) -> dict:
    g_u = float(exact_readout["g_u"])
    g_d = float(exact_readout["g_d"])
    g_ch = float(shared_norm["g_ch"])
    a_ud = float(mean_split["A_ud_candidate"])
    b_ud = float(mean_split["B_ud_candidate"])

    log_shift_u = math.log(g_u / g_ch)
    log_shift_d = math.log(g_d / g_ch)
    sigma_seed_target = -(log_shift_u + log_shift_d) / (2.0 * a_ud)
    eta_target = (log_shift_u - log_shift_d) / (2.0 * b_ud)
    sigma_u_target = sigma_seed_target + eta_target
    sigma_d_target = sigma_seed_target - eta_target

    sigma_u_current = float(spread_map["sigma_u_total_log_per_side"])
    sigma_d_current = float(spread_map["sigma_d_total_log_per_side"])
    sigma_seed_current = 0.5 * (sigma_u_current + sigma_d_current)
    eta_current = 0.5 * (sigma_u_current - sigma_d_current)

    return {
        "artifact": "oph_quark_current_family_exact_sigma_target",
        "generated_utc": _timestamp(),
        "proof_status": "closed_current_family_sigma_target",
        "theorem_scope": "current_family_only",
        "public_promotion_allowed": False,
        "supporting_artifacts": {
            "exact_readout": exact_readout["artifact"],
            "shared_norm_binding": shared_norm["artifact"],
            "sector_mean_split": mean_split["artifact"],
            "spread_map": spread_map["artifact"],
        },
        "theorem_statement": (
            "Fix the current-family affine readout law "
            "log(g_u / g_ch) = -(A_ud * sigma_seed_ud - B_ud * eta_ud) and "
            "log(g_d / g_ch) = -(A_ud * sigma_seed_ud + B_ud * eta_ud), with "
            "A_ud = 1 / (2 * (1 + rho_ord - x2^2)) and "
            "B_ud = 1 / (2 * (1 - x2^2 - x2^2 / (1 + rho_ord))). "
            "On the exact current-family quark readout witness, the unique sigma target that reproduces the "
            "exact sector means is therefore obtained by solving the two affine equations for "
            "(sigma_seed_ud, eta_ud), equivalently (sigma_u, sigma_d)."
        ),
        "fixed_affine_readout_law": {
            "A_ud": a_ud,
            "B_ud": b_ud,
            "g_ch": g_ch,
            "log_shift_u": log_shift_u,
            "log_shift_d": log_shift_d,
            "equations": [
                "log(g_u / g_ch) = -(A_ud * sigma_seed_ud - B_ud * eta_ud)",
                "log(g_d / g_ch) = -(A_ud * sigma_seed_ud + B_ud * eta_ud)",
            ],
        },
        "unique_exact_sigma_target": {
            "sigma_seed_ud_target": sigma_seed_target,
            "eta_ud_target": eta_target,
            "sigma_u_target": sigma_u_target,
            "sigma_d_target": sigma_d_target,
        },
        "current_theorem_grade_sigma_pair": {
            "sigma_seed_ud_current": sigma_seed_current,
            "eta_ud_current": eta_current,
            "sigma_u_current": sigma_u_current,
            "sigma_d_current": sigma_d_current,
        },
        "delta_vs_current_theorem_grade_sigma_pair": {
            "sigma_seed_ud": sigma_seed_target - sigma_seed_current,
            "eta_ud": eta_target - eta_current,
            "sigma_u": sigma_u_target - sigma_u_current,
            "sigma_d": sigma_d_target - sigma_d_current,
        },
        "interpretation": {
            "current_family_exact_value_target": "If the fixed A_ud/B_ud affine readout law is retained, any theorem-grade lift to exact current-family quark values must emit this sigma target or an equivalent sigma datum.",
            "next_public_bridge": "quark_physical_sigma_ud_lift",
            "next_public_bridge_role": "target-free sector-attached lift whose emitted physical sigma datum can be compared against the exact sigma target recorded here.",
        },
        "do_not_claim_now": [
            "that the theorem-grade physical sigma pair already equals this target",
            "that Theta_ud^phys is proved by the current-family sigma target alone",
        ],
        "notes": [
            "This is a current-family exact target extracted from the exact readout witness and the fixed affine mean law.",
            "It sharpens the physical-sheet search by converting the remaining sigma burden into an explicit quantitative target.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the exact current-family sigma target artifact.")
    parser.add_argument("--exact-readout", default=str(EXACT_READOUT_JSON))
    parser.add_argument("--shared-norm", default=str(SHARED_NORM_JSON))
    parser.add_argument("--mean-split", default=str(MEAN_SPLIT_JSON))
    parser.add_argument("--spread-map", default=str(SPREAD_MAP_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    artifact = build_artifact(
        json.loads(Path(args.exact_readout).read_text(encoding="utf-8")),
        json.loads(Path(args.shared_norm).read_text(encoding="utf-8")),
        json.loads(Path(args.mean_split).read_text(encoding="utf-8")),
        json.loads(Path(args.spread_map).read_text(encoding="utf-8")),
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
