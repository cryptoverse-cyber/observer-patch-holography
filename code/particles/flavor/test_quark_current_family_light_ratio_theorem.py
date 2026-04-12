#!/usr/bin/env python3
"""Validate the exact current-family light-ratio theorem artifact."""

from __future__ import annotations

import json
import math
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
SPREAD_SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_spread_map.py"
MEAN_SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_sector_mean_split.py"
QUADRATIC_SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_current_family_quadratic_readout_theorem.py"
EXACT_SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_current_family_exact_readout.py"
SELECTOR_SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_relative_sheet_selector.py"
PHYSICAL_BRANCH_SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_physical_branch_repair_theorem.py"
SELECTED_SHEET_SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_current_family_selected_sheet_closure.py"
SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_current_family_light_ratio_theorem.py"
OUTPUT = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_light_ratio_theorem.json"


def test_quark_current_family_light_ratio_theorem() -> None:
    subprocess.run([sys.executable, str(SPREAD_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(MEAN_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(QUADRATIC_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(EXACT_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(SELECTOR_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(PHYSICAL_BRANCH_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(SELECTED_SHEET_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(SCRIPT)], check=True, cwd=ROOT)

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))

    assert payload["artifact"] == "oph_quark_current_family_light_ratio_theorem"
    assert payload["proof_status"] == "closed_current_family_light_ratio_theorem"
    assert payload["theorem_scope"] == "current_family_only"
    assert payload["public_promotion_allowed"] is False

    exact = payload["exact_light_data"]
    decomp = payload["exact_readout_decomposition"]
    ell = float(exact["ell_ud"])
    assert math.isclose(float(decomp["ell_ud_from_decomposition"]), ell, rel_tol=0.0, abs_tol=1e-15)
    assert math.isclose(float(decomp["decomposition_residual"]), 0.0, rel_tol=0.0, abs_tol=1e-15)
    assert payload["next_bridge_to_public_frontier"]["public_missing_object"] == "light_quark_overlap_defect_value_law"
