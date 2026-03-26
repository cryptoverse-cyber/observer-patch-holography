#!/usr/bin/env python3
"""Run the quenched hadron reference lane from the compact public export.

This is a thin subprocess wrapper around the canonical OPH reference script:
`code/particles/core/oph_lattice_su3_quenched_v5.py`.

The wrapper keeps all physics and numerical parameters explicit and stores a
structured JSON artifact under `runs/`.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List


ROOT = pathlib.Path(__file__).resolve().parents[1]
REFERENCE_SCRIPT = ROOT / "core" / "oph_lattice_su3_quenched_v5.py"
DEFAULT_RUN_DIR = ROOT /  "runs" / "hadron"


def _split_csv(value: str) -> List[float]:
    values = [item.strip() for item in value.split(",") if item.strip()]
    if not values:
        raise argparse.ArgumentTypeError("expected a non-empty comma-separated list")
    try:
        return [float(item) for item in values]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid comma-separated float list: {value!r}") from exc


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the quenched hadron reference lane and save a JSON artifact."
    )
    parser.add_argument("--python", default=sys.executable, help="Python interpreter to use for the canonical script.")
    parser.add_argument("--reference-script", default=str(REFERENCE_SCRIPT), help="Path to the canonical quenched hadron script.")
    parser.add_argument("--out", default="", help="Output JSON path. Defaults to runs/hadron/<timestamp>.json")
    parser.add_argument("--beta", type=float, default=5.7)
    parser.add_argument("--L", type=int, default=4)
    parser.add_argument("--T", type=int, default=8)
    parser.add_argument("--therm", type=int, default=10)
    parser.add_argument("--sweeps", type=int, default=30)
    parser.add_argument("--every", type=int, default=5)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--kappas", type=_split_csv, default=_split_csv("0.120,0.125"), help="Comma-separated kappas, for example 0.120,0.125.")
    parser.add_argument("--nf", type=int, default=0, help="Active flavours for the MS-bar beta function.")
    parser.add_argument("--c-flow", dest="c_flow", type=float, default=0.3, help="Flow parameter used by the reference lane.")
    parser.add_argument("--eps-flow", dest="eps_flow", type=float, default=0.01, help="Flow integrator step size.")
    parser.add_argument("--json-only", action="store_true", help="Print only the parsed JSON result to stdout.")
    return parser


def build_command(args: argparse.Namespace) -> List[str]:
    return [
        args.python,
        args.reference_script,
        "--beta",
        str(args.beta),
        "--L",
        str(args.L),
        "--T",
        str(args.T),
        "--therm",
        str(args.therm),
        "--sweeps",
        str(args.sweeps),
        "--every",
        str(args.every),
        "--seed",
        str(args.seed),
        "--kappas",
        ",".join(f"{value:g}" for value in args.kappas),
        "--nf",
        str(args.nf),
        "--c",
        str(args.c_flow),
        "--eps",
        str(args.eps_flow),
        "--json",
    ]


def default_output_path() -> pathlib.Path:
    DEFAULT_RUN_DIR.mkdir(parents=True, exist_ok=True)
    return DEFAULT_RUN_DIR / f"quenched-reference-{_timestamp()}.json"


def load_json_text(text: str) -> Dict[str, Any]:
    return json.loads(text)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    reference_script = pathlib.Path(args.reference_script)
    if not reference_script.exists():
        parser.error(f"reference script not found: {reference_script}")

    out_path = pathlib.Path(args.out) if args.out else default_output_path()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = build_command(args)
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)

    result: Dict[str, Any] | None = None
    parse_error: str | None = None
    if proc.stdout.strip():
        try:
            result = load_json_text(proc.stdout)
        except json.JSONDecodeError as exc:
            parse_error = f"{exc.msg} at line {exc.lineno} column {exc.colno}"

    payload: Dict[str, Any] = {
        "runner": {
            "script": str(pathlib.Path(__file__).resolve()),
            "cwd": os.getcwd(),
            "created_utc": _timestamp(),
        },
        "reference_script": str(reference_script),
        "command": cmd,
        "parameters": {
            "beta": args.beta,
            "L": args.L,
            "T": args.T,
            "therm": args.therm,
            "sweeps": args.sweeps,
            "every": args.every,
            "seed": args.seed,
            "kappas": args.kappas,
            "nf": args.nf,
            "c_flow": args.c_flow,
            "eps_flow": args.eps_flow,
        },
        "subprocess": {
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        },
        "result": result,
        "parse_error": parse_error,
    }

    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.json_only:
        sys.stdout.write(json.dumps(result if result is not None else payload, indent=2, sort_keys=True))
        if sys.stdout.isatty():
            sys.stdout.write("\n")
    else:
        print(f"saved: {out_path}")
        print(f"returncode: {proc.returncode}")
        if parse_error:
            print(f"parse_error: {parse_error}")
        elif result is not None:
            print("result keys:", ", ".join(sorted(result.keys())))

    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
