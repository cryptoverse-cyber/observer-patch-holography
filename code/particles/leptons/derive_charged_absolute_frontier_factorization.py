#!/usr/bin/env python3
"""Emit the layered charged absolute-frontier factorization artifact."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from charged_absolute_route_common import (
    ABSOLUTE_FRONTIER_FACTORIZATION_JSON,
    POST_PROMOTION_ROUTE_JSON,
    UNDERDETERMINATION_JSON,
    load_json,
)


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_artifact(underdetermination: dict, route: dict) -> dict:
    current_surface_contract = underdetermination.get("future_single_slot_only", {})
    current_surface_minimal = underdetermination.get("minimal_new_theorem", {})
    post_promotion_slot = route.get("post_promotion_single_slot", {})
    induced = route.get("induced_once_post_promotion_slot_exists", {})

    return {
        "artifact": "oph_charged_absolute_frontier_factorization",
        "generated_utc": _timestamp(),
        "status": "layered_frontier_factorization_closed",
        "public_promotion_allowed": False,
        "summary": (
            "The charged absolute frontier is layered. On the current common-shift quotient "
            "surface the exact missing affine object is A_ch. Conditional on future centered "
            "promotion, that absolute-side burden reduces further: the only irreducible "
            "post-promotion slot is the refinement-stable uncentered trace lift, from which "
            "the determinant-line section and A_ch are induced."
        ),
        "current_surface_layer": {
            "current_theorem_output": underdetermination.get("theorem_emit", {}).get("meaning"),
            "exact_missing_object": underdetermination.get("next_exact_missing_object"),
            "required_contract": current_surface_contract.get("required_contract"),
            "required_new_scalar": current_surface_minimal.get("required_new_scalar"),
            "why_this_layer_exists": (
                "The current theorem surface emits only the common-shift quotient class, so an "
                "affine-covariant absolute coordinate is absent and must be added before any "
                "theorem-grade absolute charged scale can be read out."
            ),
        },
        "post_promotion_layer": {
            "condition": "assuming theorem_grade_C_hat_e has been promoted on theorem-grade physical Y_e",
            "promotion_only_no_go": route.get("promotion_only_no_go"),
            "irreducible_single_slot": {
                "id": post_promotion_slot.get("id"),
                "artifact": post_promotion_slot.get("artifact"),
                "artifact_ref": post_promotion_slot.get("artifact_ref"),
                "required_contract": post_promotion_slot.get("must_emit"),
                "required_properties": post_promotion_slot.get("must_satisfy"),
                "internal_carrier": post_promotion_slot.get("internal_carrier"),
                "internal_scalarization_artifact_ref": post_promotion_slot.get(
                    "internal_scalarization_artifact_ref"
                ),
                "exact_descended_scalar": post_promotion_slot.get("exact_descended_scalar"),
                "exact_smaller_forcing_object": post_promotion_slot.get("exact_smaller_forcing_object"),
            },
            "induced_after_single_slot": induced,
        },
        "frontier_ledger": {
            "do_not_conflate": [
                "charged_absolute_anchor_A_ch as current-surface missing affine object",
                "refinement_stable_uncentered_trace_lift as the post-promotion single slot",
            ],
            "current_surface_missing_object": underdetermination.get("next_exact_missing_object"),
            "post_promotion_single_slot": post_promotion_slot.get("id"),
            "post_promotion_exact_descended_scalar": post_promotion_slot.get("exact_descended_scalar", {}).get("id"),
            "post_promotion_exact_smaller_forcing_object": post_promotion_slot.get(
                "exact_smaller_forcing_object", {}
            ).get("id"),
            "reduction_theorem_id": route.get("reduction_theorem", {}).get("id"),
        },
        "theorem_statement": (
            "The current charged absolute no-go and the sharpened post-promotion route solve "
            "different layers of the lane. The current layer identifies the absent affine "
            "coordinate A_ch on the common-shift quotient surface. After centered promotion, "
            "the absolute tail reduces canonically to one refinement-stable uncentered trace "
            "lift, which then induces the determinant-line section, A_ch, and the absolute "
            "charged outputs. Therefore the supported charged absolute frontier is layered rather "
            "than a single bare A_ch slot."
        ),
        "notes": [
            "This artifact does not promote any current-corpus absolute closure.",
            "It exists to prevent mixing the current-surface no-go with the sharper post-promotion reduction route.",
            "The post-promotion slot is still a single slot, but it now has an exact scalar-cocycle carrier rather than a vague matrix-level ambiguity.",
            "A separate no-go is now explicit too: promotion of centered C_hat_e alone still cannot emit mu_phys(Y_e).",
            "Under the refinement-stability clause already built into that slot, the remaining burden descends to one physical affine scalar mu_phys(Y_e), with the physical identity-mode equalizer as the exact smaller forcing object beneath it.",
            "Same-carrier eta/sigma residuals remain separate from this theorem-facing absolute-side factorization.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the layered charged absolute-frontier factorization artifact.")
    parser.add_argument("--underdetermination", default=str(UNDERDETERMINATION_JSON))
    parser.add_argument("--route", default=str(POST_PROMOTION_ROUTE_JSON))
    parser.add_argument("--output", default=str(ABSOLUTE_FRONTIER_FACTORIZATION_JSON))
    args = parser.parse_args()

    artifact = build_artifact(
        load_json(Path(args.underdetermination)),
        load_json(Path(args.route)),
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
