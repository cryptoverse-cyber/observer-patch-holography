#!/usr/bin/env python3
"""Validate the D12 quark physical-branch repair theorem artifact."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
BRANCH_SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_d12_mass_branch_and_ckm_residual.py"
REPAIR_SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_physical_branch_repair_theorem.py"
OUTPUT = ROOT / "particles" / "runs" / "flavor" / "quark_physical_branch_repair_theorem.json"


def test_quark_physical_branch_repair_theorem_marks_current_d12_sheet_as_no_go() -> None:
    subprocess.run([sys.executable, str(BRANCH_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(REPAIR_SCRIPT)], check=True, cwd=ROOT)

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert payload["artifact"] == "oph_quark_physical_branch_repair_theorem"
    assert payload["proof_status"] == "current_d12_sheet_is_strict_no_go_for_physical_ckm_shell"
    assert payload["current_d12_sheet"]["quark_relative_sheet_selector"] is None
    assert payload["minimal_branch_shift_repair_theorem"]["must_emit"] == "quark_relative_sheet_selector"
    assert payload["relative_sheet_scan"]["status"] == "not_available_from_current_local_solver"
    assert payload["physical_shell_mismatch"]["undershoot_factors"]["theta_12"] > 1.0
    assert payload["current_sheet_invariants"]["jarlskog_fraction_of_max_allowed_by_current_angles"] > 0.9
