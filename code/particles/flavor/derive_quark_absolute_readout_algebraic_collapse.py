#!/usr/bin/env python3
"""Emit the conditional algebraic collapse of quark absolute readout."""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SHARED_NORM_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_shared_absolute_norm_binding.json"
MEAN_SPLIT_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_sector_mean_split.json"
SIGMA_TARGET_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_exact_sigma_target.json"
EXACT_PDG_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_exact_pdg_theorem.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "flavor" / "quark_absolute_readout_algebraic_collapse.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_artifact(shared_norm: dict, mean_split: dict, sigma_target: dict, exact_pdg: dict) -> dict:
    g_ch = float(shared_norm["g_ch"])
    a_ud = float(mean_split["A_ud_candidate"])
    b_ud = float(mean_split["B_ud_candidate"])
    target = sigma_target["unique_exact_sigma_target"]
    sigma_seed = float(target["sigma_seed_ud_target"])
    eta = float(target["eta_ud_target"])
    sigma_u = float(target["sigma_u_target"])
    sigma_d = float(target["sigma_d_target"])
    g_u = g_ch * math.exp(-(a_ud * sigma_seed - b_ud * eta))
    g_d = g_ch * math.exp(-(a_ud * sigma_seed + b_ud * eta))

    return {
        "artifact": "oph_quark_absolute_readout_algebraic_collapse",
        "generated_utc": _timestamp(),
        "proof_status": "closed_algebraic_collapse_given_theorem_grade_sigma_datum",
        "theorem_scope": "conditional_on_strengthened_physical_sigma_lift",
        "public_promotion_allowed": False,
        "theorem_statement": (
            "Assume the theorem-grade shared quark normalization g_ch together with a theorem-grade physical "
            "sigma datum (sigma_u, sigma_d) on the quark physical sheet. Define "
            "sigma_seed_ud := (sigma_u + sigma_d) / 2 and eta_ud := (sigma_u - sigma_d) / 2. "
            "Then the quark absolute sector readout is algebraic:"
            " g_u = g_ch * exp(-(A_ud * sigma_seed_ud - B_ud * eta_ud)) and"
            " g_d = g_ch * exp(-(A_ud * sigma_seed_ud + B_ud * eta_ud)),"
            " where A_ud = 1 / (2 * (1 + rho_ord - x2^2)) and"
            " B_ud = 1 / (2 * (1 - x2^2 - x2^2 / (1 + rho_ord))). "
            "So once a strengthened physical sigma lift emits the physical sigma pair, the old absolute "
            "readout is no longer an independent theorem burden."
        ),
        "conditional_collapse_route": {
            "remaining_nonalgebraic_theorem": "strengthened_quark_physical_sigma_ud_lift",
            "strengthening_required": (
                "The physical lift must emit a theorem-grade physical sigma datum, equivalently "
                "a sector-attached same-label left-handed carrier element from which (sigma_u, sigma_d) are read."
            ),
            "collapsed_theorem": "quark_absolute_sector_readout_theorem",
            "why_collapsed": (
                "Given g_ch and a theorem-grade physical sigma datum, (g_u, g_d) follow by direct substitution "
                "into the fixed affine mean law."
            ),
        },
        "fixed_affine_mean_law": {
            "A_ud": a_ud,
            "B_ud": b_ud,
            "g_ch": g_ch,
            "g_u_formula": "g_ch * exp(-(A_ud * sigma_seed_ud - B_ud * eta_ud))",
            "g_d_formula": "g_ch * exp(-(A_ud * sigma_seed_ud + B_ud * eta_ud))",
        },
        "exact_current_family_sigma_specialization": {
            "sigma_u_target": sigma_u,
            "sigma_d_target": sigma_d,
            "sigma_seed_ud_target": sigma_seed,
            "eta_ud_target": eta,
            "g_u_forced": g_u,
            "g_d_forced": g_d,
        },
        "exact_current_family_pdg_consequence": {
            "artifact": exact_pdg["artifact"],
            "reconstructed_current_family_running_values_gev": exact_pdg["reconstructed_current_family_running_values_gev"],
            "note": (
                "Specializing the conditional algebraic readout to the exact current-family sigma target reproduces "
                "the exact current-family PDG-matched running values already recorded on the witness surface."
            ),
        },
        "candidate_merged_theorem_text": (
            "A strengthened quark physical sigma lift emits a sector-attached same-label left-handed physical datum "
            "together with the theorem-grade physical sigma pair (sigma_u, sigma_d). With theorem-grade g_ch already available, "
            "the affine mean law algebraically emits (g_u, g_d), hence the ordered three-point readout emits the quark sextet."
        ),
        "do_not_claim_now": [
            "that the strengthened physical sigma lift is already proved",
            "that the public quark lane is already reduced to one proved theorem",
        ],
        "notes": [
            "This artifact proves the algebraic part of the proposed one-theorem compression route.",
            "It does not prove the nonalgebraic physical sigma lift itself.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the quark absolute-readout algebraic collapse artifact.")
    parser.add_argument("--shared-norm", default=str(SHARED_NORM_JSON))
    parser.add_argument("--mean-split", default=str(MEAN_SPLIT_JSON))
    parser.add_argument("--sigma-target", default=str(SIGMA_TARGET_JSON))
    parser.add_argument("--exact-pdg", default=str(EXACT_PDG_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    artifact = build_artifact(
        json.loads(Path(args.shared_norm).read_text(encoding="utf-8")),
        json.loads(Path(args.mean_split).read_text(encoding="utf-8")),
        json.loads(Path(args.sigma_target).read_text(encoding="utf-8")),
        json.loads(Path(args.exact_pdg).read_text(encoding="utf-8")),
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
