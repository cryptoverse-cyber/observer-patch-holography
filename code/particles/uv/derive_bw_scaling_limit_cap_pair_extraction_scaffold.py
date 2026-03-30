#!/usr/bin/env python3
"""Emit the canonical scaling-limit cap-pair extraction scaffold."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "particles" / "runs" / "uv" / "bw_scaling_limit_cap_pair_extraction_scaffold.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_payload() -> dict[str, object]:
    return {
        "artifact": "oph_bw_scaling_limit_cap_pair_extraction_scaffold",
        "generated_utc": _timestamp(),
        "status": "candidate_route_not_promoted",
        "public_promotion_allowed": False,
        "exact_missing_object": "scaling_limit_cap_pair_extraction",
        "goal": (
            "Extract a canonical scaling-limit cap pair (A_infty(C), omega_infty^C) "
            "from transported cap marginals along the realized refinement-stable branch."
        ),
        "input_contract": {
            "must_use": [
                "transported_cap_marginals along a realized refinement chain",
                "inherited strip data with oriented null generator and ordered cut pair",
                "support-map control on the quasi-local cap net",
            ],
            "must_not_assume": [
                "type-I survival in the scaling limit",
                "a pre-existing BW automorphism theorem",
                "a fixed-cutoff density-matrix identification of the limit",
            ],
        },
        "checks": [
            "local_weak_star_extraction",
            "vanishing_carried_collar_errors",
            "refinement_stable_transport_compatibility",
            "uniqueness_of_extracted_limit_action",
        ],
        "output_certificate": {
            "extracted_pair": "(A_infty(C), omega_infty^C)",
            "typeI_required": False,
            "residual_modular_class": "q_BW(C) remains open until ordered-cut rigidity closes",
            "status_on_fill": "realized_limit_pair_closed",
        },
        "follow_on_object": {
            "id": "ordered_null_cut_pair_rigidity",
            "role": (
                "Collapse the residual cap-preserving conformal freedom on the realized "
                "limit pair to the unique BW hyperbolic subgroup."
            ),
        },
        "final_target": "sigma_t^{omega_infty^C} = alpha_{lambda_C(2 pi t)}",
        "notes": [
            "This is the first half of the UV/BW internalization route.",
            "It does not by itself prove the BW automorphism law.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the BW scaling-limit cap-pair extraction scaffold.")
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    payload = build_payload()
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
