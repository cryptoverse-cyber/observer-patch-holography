#!/usr/bin/env python3
"""Emit the exact light-ratio theorem on the restricted transport-frame carrier."""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PDG_COMPLETION_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_transport_frame_exact_pdg_completion.json"
DEFAULT_OUT = (
    ROOT / "particles" / "runs" / "flavor" / "quark_current_family_transport_frame_light_ratio_theorem.json"
)


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_artifact(pdg_completion: dict) -> dict:
    masses = dict(pdg_completion["exact_running_values_gev"])
    m_u = float(masses["u"])
    m_d = float(masses["d"])
    ell_ud = math.log(m_d / m_u)
    return {
        "artifact": "oph_quark_current_family_transport_frame_light_ratio_theorem",
        "generated_utc": _timestamp(),
        "proof_status": "closed_current_family_transport_frame_light_ratio_theorem",
        "theorem_scope": pdg_completion["theorem_scope"],
        "public_promotion_allowed": False,
        "supporting_exact_pdg_completion_artifact": pdg_completion["artifact"],
        "theorem_statement": (
            "On the explicit current-family common-refinement transport-frame carrier, the exact running quark values "
            "determine the exact light-ratio scalar ell_ud := log(m_d / m_u)."
        ),
        "exact_light_data": {
            "m_u": m_u,
            "m_d": m_d,
            "m_d_over_m_u": m_d / m_u,
            "m_u_over_m_d": m_u / m_d,
            "ell_ud": ell_ud,
        },
        "notes": [
            "This is the restricted-carrier light-ratio theorem above the exact transport-frame PDG completion surface.",
            "It does not claim target-free public promotion to H_mass := log(c_d / c_u).",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the restricted-carrier quark light-ratio theorem artifact.")
    parser.add_argument("--pdg-completion", default=str(PDG_COMPLETION_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    payload = build_artifact(_load_json(Path(args.pdg_completion)))
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
