#!/usr/bin/env python3
"""Validate the continuation-only D12 internal-backread forward Yukawas."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
DESCENT_SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_d12_internal_backread_descent.py"
FORWARD_SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_d12_internal_backread_forward_yukawas.py"
DESCENT_OUTPUT = ROOT / "particles" / "runs" / "flavor" / "quark_d12_internal_backread_descent.json"
FORWARD_OUTPUT = ROOT / "particles" / "runs" / "flavor" / "quark_d12_internal_backread_forward_yukawas.json"


def main() -> int:
    subprocess.run([sys.executable, str(DESCENT_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(FORWARD_SCRIPT)], check=True, cwd=ROOT)

    descent = json.loads(DESCENT_OUTPUT.read_text(encoding="utf-8"))
    forward = json.loads(FORWARD_OUTPUT.read_text(encoding="utf-8"))

    if descent.get("artifact") != "oph_quark_d12_internal_backread_descent":
        print("wrong D12 internal-backread descent artifact id", file=sys.stderr)
        return 1
    if descent.get("exact_missing_object") is not None:
        print("continuation-only backread descent should not leave an exact missing object open on its own sidecar inputs", file=sys.stderr)
        return 1
    if descent.get("even_excitation_proof_status") != "closed":
        print("continuation-only backread descent should close the even excitation slot on its sidecar surface", file=sys.stderr)
        return 1
    if descent.get("J_B_source_u") is None or descent.get("J_B_source_d") is None:
        print("continuation-only backread descent should carry the emitted pure-B source values", file=sys.stderr)
        return 1

    if forward.get("artifact") != "oph_quark_d12_internal_backread_forward_yukawas":
        print("wrong D12 internal-backread forward Yukawas artifact id", file=sys.stderr)
        return 1
    if forward.get("scope") != "D12_continuation_internal_backread_only":
        print("continuation-only backread forward Yukawas should remain on the sidecar scope", file=sys.stderr)
        return 1
    if forward.get("forward_certified") is not True:
        print("continuation-only backread forward Yukawas should be certified on their own sidecar inputs", file=sys.stderr)
        return 1
    if forward.get("certification_status") != "forward_matrix_certified":
        print("continuation-only backread forward Yukawas should emit a certified forward matrix surface", file=sys.stderr)
        return 1
    if forward.get("promotion_blockers") != []:
        print("continuation-only backread forward Yukawas should not carry placeholder blockers", file=sys.stderr)
        return 1
    if any(value <= 0.0 for value in forward["singular_values_u"] + forward["singular_values_d"]):
        print("continuation-only backread forward Yukawas should emit positive singular values", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
