#!/usr/bin/env python3
"""Emit the exact forward-Yukawa theorem on the declared current-family transport-frame carrier."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FORWARD_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_transport_frame_exact_forward_yukawas.json"
CHAIN_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_end_to_end_exact_pdg_derivation_chain.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_transport_frame_exact_yukawa_theorem.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_artifact(forward: dict, chain: dict) -> dict:
    return {
        "artifact": "oph_quark_current_family_transport_frame_exact_yukawa_theorem",
        "generated_utc": _timestamp(),
        "proof_status": "closed_current_family_transport_frame_exact_yukawa_theorem",
        "target_name": "exact_forward_quark_yukawas_on_declared_current_family_transport_frame",
        "theorem_scope": "current_family_common_refinement_transport_frame_only",
        "public_promotion_allowed": False,
        "supporting_artifacts": {
            "exact_forward_yukawas": forward["artifact"],
            "end_to_end_exact_chain": chain["artifact"],
        },
        "theorem_statement": (
            "On the declared current-family/common-refinement transport-frame carrier, the OPH bridge theorem, "
            "the strengthened transport-frame physical sigma lift, the algebraic absolute readout, and the exact "
            "running-value completion jointly emit explicit forward Yukawa matrices Y_u and Y_d with certified "
            "singular values equal to the exact running quark sextet on that carrier."
        ),
        "forward_yukawa_artifact": {
            "artifact": forward["artifact"],
            "scope": forward["scope"],
            "forward_certified": forward["forward_certified"],
            "certification_status": forward["certification_status"],
            "Y_u": forward["Y_u"],
            "Y_d": forward["Y_d"],
            "V_CKM": forward["V_CKM"],
            "jarlskog": forward["jarlskog"],
            "singular_values_u": forward["singular_values_u"],
            "singular_values_d": forward["singular_values_d"],
        },
        "source_chain_artifact": chain["artifact"],
        "minimal_exact_blocker_set": [],
        "strengthening_above_target": {
            "status": "separate_question",
            "name": "target_free_public_physical_sheet_yukawa_promotion",
            "note": (
                "This theorem closes the exact forward Yukawa package only on the declared "
                "current-family/common-refinement transport-frame carrier. Promoting it to a target-free "
                "public physical-sheet theorem remains a separate strengthening question."
            ),
        },
        "notes": [
            "This is the theorem wrapper for the exact transport-frame forward Yukawa artifact.",
            "It does not claim target-free public physical-sheet promotion.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the exact current-family transport-frame Yukawa theorem artifact.")
    parser.add_argument("--forward", default=str(FORWARD_JSON))
    parser.add_argument("--chain", default=str(CHAIN_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    payload = build_artifact(
        _load_json(Path(args.forward)),
        _load_json(Path(args.chain)),
    )
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
