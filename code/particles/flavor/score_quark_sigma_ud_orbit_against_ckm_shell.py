#!/usr/bin/env python3
"""Compare-only scorer for a future sigma_ud orbit.

This helper does not emit a theorem-grade selector. It only ranks already
enumerated orbit elements against the debug CKM shell once a finite orbit has
been exposed.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ORBIT_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_sigma_ud_orbit.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "flavor" / "quark_sigma_ud_orbit_scored.json"

TARGET = {
    "theta_12": 0.2256,
    "theta_23": 0.0438,
    "theta_13": 0.00347,
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _loss(item: dict[str, Any]) -> float | None:
    try:
        inv = item.get("ckm_invariants") or item.get("ckm")
        return sum((float(inv[key]) - TARGET[key]) ** 2 for key in TARGET)
    except Exception:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Score a quark sigma_ud orbit against the debug CKM shell.")
    parser.add_argument("--orbit", default=str(ORBIT_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    orbit = _load_json(Path(args.orbit))
    ranked = []
    for item in orbit.get("elements", []):
        loss = _loss(item)
        ranked.append(
            {
                "sigma_id": item.get("sigma_id"),
                "canonical_token": item.get("canonical_token"),
                "branch_key": item.get("branch_key"),
                "loss": loss,
                "ckm_invariants": item.get("ckm_invariants") or item.get("ckm"),
            }
        )

    ranked.sort(key=lambda item: (math.inf if item["loss"] is None else item["loss"], str(item["sigma_id"])))

    artifact = {
        "artifact": "oph_quark_sigma_ud_orbit_scored",
        "status": "compare_only",
        "public_promotion_allowed": False,
        "must_not_promote_selector": True,
        "input_artifact": orbit.get("artifact"),
        "target_shell": TARGET,
        "ranked_elements": ranked,
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
