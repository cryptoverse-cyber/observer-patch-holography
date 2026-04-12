#!/usr/bin/env python3
"""Emit the single end-to-end exact-PDG quark theorem on the explicit chain."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHAIN_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_end_to_end_exact_pdg_derivation_chain.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "flavor" / "quark_exact_pdg_end_to_end_theorem.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_artifact(chain: dict) -> dict:
    return {
        "artifact": "oph_quark_exact_pdg_end_to_end_theorem",
        "generated_utc": _timestamp(),
        "proof_status": "closed_current_family_exact_pdg_end_to_end_theorem",
        "target_name": chain["target_name"],
        "theorem_scope": chain["theorem_scope"],
        "public_promotion_allowed": False,
        "supporting_chain_artifact": chain["artifact"],
        "theorem_statement": (
            "On the explicit current-family/common-refinement transport-frame chain internalized on the code surface, "
            "the OPH bridge theorem, strengthened transport-frame physical sigma lift, affine absolute readout "
            "collapse, ordered three-point readout, and exact forward-Yukawa emission jointly derive the exact "
            "current-family PDG running quark masses and explicit Yukawa matrices."
        ),
        "minimal_exact_blocker_set": chain["minimal_exact_blocker_set"],
        "exact_running_values_gev": chain["exact_running_values_gev"],
        "lemma_chain": chain["lemma_chain"],
        "strengthening_above_target": chain["strengthening_above_target"],
        "notes": [
            "This is the single theorem wrapper above the explicit exact-PDG derivation chain artifact.",
            "It records the completed exact chain on the declared surface in one place.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the end-to-end exact-PDG quark theorem artifact.")
    parser.add_argument("--chain", default=str(CHAIN_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    payload = build_artifact(_load_json(Path(args.chain)))
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
