#!/usr/bin/env python3
"""Build a conservative ground-state summary from extracted hadron artifacts."""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any


def load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_fit_summary(extracted: dict[str, Any], source_path: pathlib.Path) -> dict[str, Any]:
    channels = extracted.get("available_scalar_channels") or {}
    return {
        "source_extracted_artifact": str(source_path),
        "fit_mode": "scalar_passthrough",
        "channels": {
            "pi": {
                "estimate": channels.get("pi"),
                "fit_quality": "not_available_from_scalar_payload",
            },
            "rho_local": {
                "estimate": channels.get("rho_local"),
                "fit_quality": "not_available_from_scalar_payload",
            },
            "nucleon_local": {
                "estimate": channels.get("nucleon_local"),
                "fit_quality": "not_available_from_scalar_payload",
            },
        },
        "notes": [
            "This summary is a bookkeeping surface, not a correlated-fit result.",
            "Promote to real fit-window scans only after raw correlator arrays are stored.",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Build simple hadron ground-state summaries.")
    ap.add_argument("extracted_artifacts", nargs="+", help="Artifacts from extract_two_point_artifacts.py")
    ap.add_argument("--out-dir", default="runs/hadron/fits", help="Directory for fit summaries")
    args = ap.parse_args()

    out_dir = pathlib.Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = pathlib.Path(__file__).resolve().parents[1] / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    for value in args.extracted_artifacts:
        source_path = pathlib.Path(value)
        if not source_path.is_absolute():
            source_path = pathlib.Path(__file__).resolve().parents[1] / source_path
        payload = load_json(source_path)
        summary = build_fit_summary(payload, source_path)
        out_path = out_dir / f"{source_path.stem}.fit.json"
        out_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
