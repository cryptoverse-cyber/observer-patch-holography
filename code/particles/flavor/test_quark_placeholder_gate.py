#!/usr/bin/env python3
"""Block silent promotion of placeholder quark Yukawa artifacts."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT /  "runs" / "flavor" / "forward_yukawas.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate quark placeholder gating.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Input forward-Yukawa artifact.")
    args = parser.parse_args()

    payload = json.loads(pathlib.Path(args.input).read_text(encoding="utf-8"))
    certified = bool(payload.get("forward_certified", False))
    if certified:
        if bool(payload.get("template_amplitude_fallback_used", False)):
            print("forward_certified claimed while template amplitude fallback is still used", file=sys.stderr)
            return 1
        if not bool(payload.get("up_down_sector_distinct", False)):
            print("forward_certified claimed while u/d sectors are still cloned", file=sys.stderr)
            return 1
    print("quark placeholder gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
