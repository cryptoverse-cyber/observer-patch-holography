#!/usr/bin/env python3
"""Build a placeholder finite-volume level artifact for the rho program."""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any


def load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser(description="Write a rho level-extraction placeholder artifact.")
    ap.add_argument("--basis", default="runs/hadron/rho_operator_basis.json")
    ap.add_argument("--out", default="runs/hadron/rho_levels.json")
    args = ap.parse_args()

    basis_path = pathlib.Path(args.basis)
    if not basis_path.is_absolute():
        basis_path = pathlib.Path(__file__).resolve().parents[3] / basis_path
    out_path = pathlib.Path(args.out)
    if not out_path.is_absolute():
        out_path = pathlib.Path(__file__).resolve().parents[3] / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)

    basis = load_json(basis_path)
    payload = {
        "status": "scaffold",
        "basis_source": str(basis_path),
        "basis_status": basis.get("status"),
        "levels": [],
        "notes": [
            "No finite-volume spectrum has been extracted yet.",
            "Populate this artifact after generalized-eigenvalue / spectrum extraction work exists.",
        ],
    }
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
