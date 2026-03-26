#!/usr/bin/env python3
"""Normalize available hadron reference outputs into two-point summary artifacts."""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any


def load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_artifact(run_payload: dict[str, Any], source_path: pathlib.Path) -> dict[str, Any]:
    result = run_payload.get("result") or {}
    return {
        "source_run_artifact": str(source_path),
        "lane_status": "smoke" if float(result.get("nf", 0.0)) == 0.0 else "pilot",
        "available_scalar_channels": {
            "pi": result.get("am_pi_chiral"),
            "rho_local": result.get("am_rho_chiral"),
            "nucleon_local": result.get("am_p_chiral"),
        },
        "available_correlator_scalars": {
            "C_pi_0": result.get("C_pi_0"),
            "C_pi_1": result.get("C_pi_1"),
            "C_rho_0": result.get("C_rho_0"),
            "C_rho_1": result.get("C_rho_1"),
            "C_p_0": result.get("C_p_0"),
            "C_p_1": result.get("C_p_1"),
        },
        "dimensionless_ratios": {
            "rho_over_pi": (
                None
                if not result.get("am_pi_chiral")
                else float(result.get("am_rho_chiral", 0.0)) / float(result.get("am_pi_chiral"))
            ),
            "nucleon_over_pi": (
                None
                if not result.get("am_pi_chiral")
                else float(result.get("am_p_chiral", 0.0)) / float(result.get("am_pi_chiral"))
            ),
        },
        "limitations": [
            "Reference artifact exposes scalar channel outputs, not raw time-slice correlator arrays.",
            "No real effective-mass or fit-window scan is possible from this payload alone.",
            "Use this artifact for systematics bookkeeping and channel availability only.",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract normalized hadron two-point artifacts.")
    ap.add_argument("run_artifacts", nargs="+", help="JSON artifacts from run_quenched_reference.py")
    ap.add_argument("--out-dir", default="runs/hadron/extracted", help="Directory for extracted artifacts")
    args = ap.parse_args()

    out_dir = pathlib.Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = pathlib.Path(__file__).resolve().parents[1] / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    for value in args.run_artifacts:
        source_path = pathlib.Path(value)
        if not source_path.is_absolute():
            source_path = pathlib.Path(__file__).resolve().parents[1] / source_path
        payload = load_json(source_path)
        artifact = build_artifact(payload, source_path)
        out_path = out_dir / f"{source_path.stem}.two_point.json"
        out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
