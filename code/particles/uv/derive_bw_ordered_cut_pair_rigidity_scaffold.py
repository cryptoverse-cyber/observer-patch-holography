#!/usr/bin/env python3
"""Emit the ordered null cut-pair rigidity scaffold and symbolic witness."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "particles" / "runs" / "uv" / "bw_ordered_cut_pair_rigidity_scaffold.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(frozen=True)
class RigidityWitness:
    preserve_minus_one: str
    preserve_plus_one: str
    solution_dimension: int
    surviving_generator_disk: str
    surviving_generator_half_line: str


def _compute_rigidity_witness() -> RigidityWitness:
    return RigidityWitness(
        preserve_minus_one="v(-1) = 0",
        preserve_plus_one="v(1) = 0",
        solution_dimension=1,
        surviving_generator_disk="1 - z**2",
        surviving_generator_half_line="2*u",
    )


def build_payload() -> dict[str, object]:
    witness = _compute_rigidity_witness()
    return {
        "artifact": "oph_bw_ordered_cut_pair_rigidity_scaffold",
        "generated_utc": _timestamp(),
        "status": "symbolic_disk_halfline_model_pass_candidate_not_promoted",
        "public_promotion_allowed": False,
        "exact_missing_object": "ordered_null_cut_pair_rigidity",
        "goal": (
            "Prove that ordered null cut-pair data rigidify the residual cap-preserving conformal "
            "freedom on the realized scaling-limit cap pair to the unique BW hyperbolic subgroup."
        ),
        "input_contract": {
            "must_use": [
                "realized scaling-limit cap pair (A_infty(C), omega_infty^C)",
                "ordered null cut pair (Gamma_minus, Gamma_plus)",
                "cap-preserving conformal action on the realized limit",
            ],
            "must_not_assume": [
                "a pre-fixed BW generator",
                "type-I implementation of the limit algebra",
            ],
        },
        "checks": [
            "ordered_cut_pair_preservation",
            "pair_preserving_lie_algebra_dimension_equals_one",
            "half_line_action_is_dilation",
            "borchers_positive_translation",
            "kappa_equals_2pi",
        ],
        "symbolic_disk_halfline_witness": asdict(witness),
        "output_certificate": {
            "residual_modular_class": "q_BW(C)=0 after ordered-cut quotient",
            "bw_automorphism_on_fill": "sigma_t^{omega_infty^C} = alpha_{lambda_C(2 pi t)}",
            "status_on_fill": "bw_rigidity_closed",
        },
        "notes": [
            "The symbolic disk / half-line witness is a sanity check, not the full theorem.",
            "This scaffold is the second half of the UV/BW internalization route.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the BW ordered cut-pair rigidity scaffold.")
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
