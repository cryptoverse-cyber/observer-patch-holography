#!/usr/bin/env python3
"""Emit the minimal charged central-split transfer extension route.

This does not promote `C_hat_e^{cand}` on the live corpus. It records the
smallest theorem extension identified by the worker bundles: a centered
Schur-type P->Q->P transfer theorem with a refinement-uniform middle-factor
bound.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
GENERATOR_JSON = ROOT / "particles" / "runs" / "flavor" / "generation_bundle_branch_generator.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "flavor" / "charged_central_split_transfer_extension.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_artifact(generator: dict[str, Any]) -> dict[str, Any]:
    transfer = dict(generator["actual_generator_transfer_candidate"])
    gaps = dict(generator["persistent_gap_certificate"])
    charged = dict(generator["charged_sector_response_operator_candidate"])
    defect_sup = float(gaps["conjugacy_defect_sup"])
    gap_lower = float(gaps["conservative_gap_lower_bound"])
    threshold = gap_lower / (2.0 * defect_sup * defect_sup) if defect_sup > 0.0 else None

    return {
        "artifact": "oph_charged_central_split_transfer_extension",
        "generated_utc": _timestamp(),
        "status": "proved_as_minimal_extension",
        "public_promotion_allowed": False,
        "extension_kind": "minimal_theorem_extension",
        "theorem": {
            "id": "central_split_quadratic_commutator_transfer",
            "statement": (
                "Assume the actual centered compressed generator has centered Schur-type form "
                "C_act = cent(PDP + PDQ Theta QDP) with refinement-uniform ||Theta|| <= M and proxy "
                "C_proxy = cent(PDP). Then exact vanishing holds when [P,D] = 0, while otherwise "
                "||C_act - C_proxy|| <= 2 M ||[P,D]||^2 and "
                "||[C_act, C_proxy]|| <= 4 M ||C_proxy|| ||[P,D]||^2."
            ),
            "hypotheses": [
                "P_r rank-3 realized bundle projector",
                "Q_r = I - P_r",
                "D_r selfadjoint descendant law",
                "C_r^act = cent(P_r D_r P_r + P_r D_r Q_r Theta_r Q_r D_r P_r)",
                "C_r^proxy = cent(P_r D_r P_r)",
                "sup_r ||Theta_r|| <= M",
            ],
            "conclusions": [
                "if [P_r,D_r] = 0 then C_r^act = C_r^proxy",
                "||C_r^act - C_r^proxy|| <= 2 M ||[P_r,D_r]||^2",
                "||[C_r^act,C_r^proxy]|| <= 4 M ||C_r^proxy|| ||[P_r,D_r]||^2",
                "first_order_residual_after_central_split = vanishes_if_commutator_zero",
                "all surviving centered P_r->P_r corrections factor through P_r->Q_r->P_r",
            ],
        },
        "live_bridge_alignment": {
            "candidate_id": transfer["candidate_id"],
            "bridge_strategy": transfer["bridge_strategy"],
            "current_strength_statement": transfer["current_strength_statement"],
            "smaller_exact_missing_clause": transfer["smaller_exact_missing_clause"],
        },
        "local_numeric_promotion_test": {
            "defect_sup": defect_sup,
            "base_min_gap": float(gaps["base_min_gap"]),
            "conservative_gap_lower_bound": gap_lower,
            "same_label_overlaps": generator["projective_readout_certificate"]["same_label_overlap_amplitudes"],
            "sufficient_uniform_constant_bound": threshold,
        },
        "promotion_effect_if_internalized": {
            "actual_generator_transfer_candidate": {
                "proof_status": "theorem_extension_ready",
                "exact_vanishing_proved": "true_under_extension_when_commutator_zero",
                "uniform_quadratic_smallness_proved": "true_under_extension_with_uniform_middle_factor",
            },
            "charged_sector_response_operator_candidate": {
                "name": charged["name"],
                "declaration_status": "promotable_once_transfer_extension_certified",
                "promotion_effect": "theorem_grade_C_hat_e",
            },
        },
        "remaining_object_after_extension": {
            "id": "charged_absolute_anchor_A_ch",
            "required_contract": "A_ch(logm + c*(1,1,1)) = A_ch(logm) + c",
            "candidate_route": "charged_determinant_line_section",
        },
        "notes": [
            "This is an extension route, not a theorem hidden in the current corpus.",
            "Internalizing this route would promote C_hat_e^cand, but it would still not solve the affine common-shift breaker A_ch by itself.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the charged central-split transfer extension artifact.")
    parser.add_argument("--generator", default=str(GENERATOR_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    generator = _load_json(Path(args.generator))
    payload = build_artifact(generator)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
