#!/usr/bin/env python3
"""Emit the residual bridge-invariant scaffold above the closed normalizer."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
NORMALIZER = ROOT / "particles" / "runs" / "neutrino" / "same_label_overlap_defect_weight_normalizer.json"
BRIDGE_CANDIDATE = ROOT / "particles" / "runs" / "neutrino" / "neutrino_lambda_nu_bridge_candidate.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "neutrino" / "neutrino_attachment_bridge_invariant_scaffold.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload(normalizer: dict[str, Any], bridge_candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact": "oph_neutrino_attachment_bridge_invariant_scaffold",
        "generated_utc": _timestamp(),
        "status": "minimal_constructive_extension",
        "public_promotion_allowed": False,
        "exact_missing_object": "oph_neutrino_attachment_bridge_invariant",
        "closed_lower_object": normalizer.get("artifact"),
        "bridge_factor_schema": bridge_candidate.get("bridge_factor_schema"),
        "residual_invariant_symbol": "I_nu",
        "contract": {
            "must_emit": "one positive residual bridge invariant I_nu or a collapse theorem removing it",
            "must_imply": "lambda_nu = m_star_eV * F_nu(qbar, I_nu)",
            "must_not_use": [
                "external_oscillation_anchors",
                "PDG_target_backsolve",
                "PMNS_target_seed",
            ],
        },
        "collapse_alternative": "prove_F_nu_equals_F_nu(qbar)_with_no_residual_invariant",
        "notes": [
            "The normalized same-label overlap-defect weight section is already emitted below this object.",
            "This scaffold isolates the remaining positive scalar attachment content above qbar_e and below lambda_nu.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the neutrino attachment bridge-invariant scaffold.")
    parser.add_argument("--normalizer", default=str(NORMALIZER))
    parser.add_argument("--bridge-candidate", default=str(BRIDGE_CANDIDATE))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    payload = build_payload(
        normalizer=_load_json(Path(args.normalizer)),
        bridge_candidate=_load_json(Path(args.bridge_candidate)),
    )
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
