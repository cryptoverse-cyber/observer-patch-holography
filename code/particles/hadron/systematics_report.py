#!/usr/bin/env python3
"""Summarize the current hadron lane systematics status."""

from __future__ import annotations

import argparse
import json
import pathlib
from collections import Counter
from typing import Any


ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def classify_reference_artifact(payload: dict[str, Any]) -> dict[str, Any]:
    result = payload.get("result") or {}
    blockers: list[str] = []
    nf = float(result.get("nf", 0.0))
    L = float(result.get("L", 0.0))
    T = float(result.get("T", 0.0))
    n_meas = float(result.get("n_meas", 0.0))
    if nf == 0.0:
        blockers.append("quenched")
    if L <= 8 or T <= 16:
        blockers.append("tiny_debug_volume")
    if n_meas < 10.0:
        blockers.append("low_statistics")
    if result.get("am_rho_chiral") is not None:
        blockers.append("rho_not_resonance_extracted")
    if result.get("am_p_chiral") is not None:
        blockers.append("baryon_path_not_full_contractions")
    lane_status = "smoke" if blockers else "closure_candidate"
    if lane_status != "smoke" and nf > 0.0:
        lane_status = "pilot"
    return {
        "lane_status": lane_status,
        "blockers": blockers,
        "summary": {
            "nf": nf,
            "L": L,
            "T": T,
            "n_meas": n_meas,
            "am_pi_chiral": result.get("am_pi_chiral"),
            "am_rho_chiral": result.get("am_rho_chiral"),
            "am_p_chiral": result.get("am_p_chiral"),
        },
    }


def build_report(paths: list[pathlib.Path]) -> dict[str, Any]:
    runs = []
    blockers = Counter()
    statuses = Counter()
    for path in paths:
        payload = load_json(path)
        classification = classify_reference_artifact(payload)
        runs.append(
            {
                "path": str(path),
                "lane_status": classification["lane_status"],
                "blockers": classification["blockers"],
                "summary": classification["summary"],
            }
        )
        statuses[classification["lane_status"]] += 1
        blockers.update(classification["blockers"])
    return {
        "run_count": len(runs),
        "status_counts": dict(statuses),
        "common_blockers": dict(blockers),
        "promotion_verdict": "debug_only" if blockers else "closure_candidate",
        "target_order": [
            "m_pi",
            "m_N_isospin_symmetric",
            "rho_resonance",
            "p_minus_n_with_qcd_qed",
        ],
        "runs": runs,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Build a hadron systematics report.")
    ap.add_argument("artifacts", nargs="+", help="Hadron reference JSON artifacts")
    ap.add_argument("--out", default="", help="Optional JSON output path")
    args = ap.parse_args()

    paths = []
    for value in args.artifacts:
        path = pathlib.Path(value)
        if not path.is_absolute():
            path = ROOT / value
        paths.append(path)
    report = build_report(paths)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.out:
        out_path = pathlib.Path(args.out)
        if not out_path.is_absolute():
            out_path = ROOT / args.out
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
        print(out_path)
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
