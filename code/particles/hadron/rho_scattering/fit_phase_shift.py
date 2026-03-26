#!/usr/bin/env python3
"""Write a placeholder phase-shift fit artifact for the rho program."""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any


def load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser(description="Write a rho phase-shift-fit placeholder artifact.")
    ap.add_argument("--levels", default="runs/hadron/rho_levels.json")
    ap.add_argument("--out", default="runs/hadron/rho_phase_shift_fit.json")
    args = ap.parse_args()

    levels_path = pathlib.Path(args.levels)
    if not levels_path.is_absolute():
        levels_path = pathlib.Path(__file__).resolve().parents[3] / levels_path
    out_path = pathlib.Path(args.out)
    if not out_path.is_absolute():
        out_path = pathlib.Path(__file__).resolve().parents[3] / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)

    levels = load_json(levels_path)
    payload = {
        "status": "scaffold",
        "levels_source": str(levels_path),
        "levels_status": levels.get("status"),
        "fit_model": "not_yet_fit",
        "notes": [
            "Use this surface for Luescher / pole-fit metadata once finite-volume levels exist.",
            "The current local-rho effective mass is not the closure observable.",
        ],
    }
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
