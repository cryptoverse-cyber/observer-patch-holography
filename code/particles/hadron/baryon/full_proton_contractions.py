#!/usr/bin/env python3
"""Emit a scaffold plan for full proton contractions in the hadron sandbox."""

from __future__ import annotations

import argparse
import json
import pathlib


def main() -> int:
    ap = argparse.ArgumentParser(description="Write a proton contraction plan artifact.")
    ap.add_argument("--out", default="runs/hadron/proton_contraction_plan.json")
    args = ap.parse_args()

    out_path = pathlib.Path(args.out)
    if not out_path.is_absolute():
        out_path = pathlib.Path(__file__).resolve().parents[3] / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "status": "scaffold",
        "objective": "replace the current compact direct-term-only baryon path with a full proton contraction lane",
        "required_terms": [
            "direct",
            "exchange",
            "spin-color antisymmetrization",
            "source/sink smearing bookkeeping",
        ],
        "deliverables": [
            "raw contraction tensors",
            "nucleon correlators at multiple source-sink separations",
            "fit-ready metadata",
        ],
    }
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
