#!/usr/bin/env python3
"""Emit a minimal rho-scattering operator-basis plan."""

from __future__ import annotations

import argparse
import json
import pathlib


def main() -> int:
    ap = argparse.ArgumentParser(description="Write a rho operator-basis artifact.")
    ap.add_argument("--out", default="runs/hadron/rho_operator_basis.json")
    args = ap.parse_args()

    out_path = pathlib.Path(args.out)
    if not out_path.is_absolute():
        out_path = pathlib.Path(__file__).resolve().parents[3] / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "status": "scaffold",
        "target": "rho resonance via pi-pi finite-volume spectra",
        "operators": [
            "local vector interpolator",
            "two-pion operators in moving frames",
            "irrep-resolved operator sets",
        ],
        "next_outputs": [
            "basis description",
            "level-extraction inputs",
            "Luescher-fit-ready metadata",
        ],
    }
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
