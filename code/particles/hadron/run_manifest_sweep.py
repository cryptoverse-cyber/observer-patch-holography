#!/usr/bin/env python3
"""Run a manifest-driven hadron debug sweep under /particles."""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any

import yaml


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_RUNNER = ROOT /  "hadron" / "run_quenched_reference.py"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_manifest(path: pathlib.Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("manifest must be a mapping")
    runs = payload.get("runs")
    if not isinstance(runs, list) or not runs:
        raise ValueError("manifest must contain a non-empty runs list")
    return payload


def build_runner_command(
    runner: pathlib.Path,
    entry: dict[str, Any],
    output_path: pathlib.Path,
) -> list[str]:
    return [
        sys.executable,
        str(runner),
        "--out",
        str(output_path),
        "--beta",
        str(entry["beta"]),
        "--L",
        str(entry["L"]),
        "--T",
        str(entry["T"]),
        "--therm",
        str(entry["therm"]),
        "--sweeps",
        str(entry["sweeps"]),
        "--every",
        str(entry["every"]),
        "--seed",
        str(entry["seed"]),
        "--kappas",
        str(entry["kappas"]),
        "--nf",
        str(entry["nf"]),
        "--c-flow",
        str(entry.get("c_flow", 0.30)),
        "--eps-flow",
        str(entry.get("eps_flow", 0.01)),
    ]


def main() -> int:
    ap = argparse.ArgumentParser(description="Run a hadron sweep from a YAML manifest.")
    ap.add_argument("--manifest", required=True, help="YAML manifest under particles/hadron/profiles/")
    ap.add_argument("--limit", type=int, default=0, help="Optional limit on number of runs.")
    ap.add_argument("--dry-run", action="store_true", help="Print planned runs without executing them.")
    ap.add_argument("--continue-on-error", action="store_true", help="Continue after a failed subprocess.")
    args = ap.parse_args()

    manifest_path = pathlib.Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = ROOT / manifest_path
    manifest = load_manifest(manifest_path)
    runner = DEFAULT_RUNNER
    output_root = ROOT / str(manifest.get("output_root") or "runs/hadron/sweeps")
    sweep_dir = output_root / f"{manifest_path.stem}-{utc_stamp()}"
    entries_dir = sweep_dir / "entries"
    entries_dir.mkdir(parents=True, exist_ok=True)

    selected = manifest["runs"][: args.limit] if args.limit and args.limit > 0 else manifest["runs"]
    index: dict[str, Any] = {
        "generated_at": utc_stamp(),
        "manifest_path": str(manifest_path),
        "profile_name": manifest.get("profile_name", manifest_path.stem),
        "description": manifest.get("description", ""),
        "sweep_dir": str(sweep_dir),
        "runs": [],
    }
    (sweep_dir / "manifest.resolved.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    overall_status = 0
    for entry in selected:
        run_id = str(entry["id"])
        output_path = entries_dir / f"{run_id}.json"
        record: dict[str, Any] = {
            "id": run_id,
            "tags": entry.get("tags", []),
            "kind": entry.get("kind", "quenched_reference"),
            "output_path": str(output_path),
        }
        if record["kind"] != "quenched_reference":
            record["status"] = "skipped_non_quenched_kind"
            index["runs"].append(record)
            continue
        cmd = build_runner_command(runner, entry, output_path)
        record["command"] = cmd
        if args.dry_run:
            record["status"] = "planned"
            index["runs"].append(record)
            continue
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        record["returncode"] = proc.returncode
        record["stdout"] = proc.stdout
        record["stderr"] = proc.stderr
        record["status"] = "completed" if proc.returncode == 0 else "failed"
        index["runs"].append(record)
        if proc.returncode != 0:
            overall_status = proc.returncode
            if not args.continue_on_error:
                break

    (sweep_dir / "index.json").write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"sweep_dir: {sweep_dir}")
    print(f"runs_recorded: {len(index['runs'])}")
    return overall_status


if __name__ == "__main__":
    raise SystemExit(main())
