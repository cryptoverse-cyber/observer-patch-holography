#!/usr/bin/env python3
"""Validate the exact current-family quark sigma target artifact."""

from __future__ import annotations

import json
import math
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
EXACT_SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_current_family_exact_readout.py"
SHARED_NORM_SCRIPT = ROOT / "particles" / "flavor" / "derive_charged_shared_absolute_scale_writeback.py"
MEAN_SPLIT_SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_sector_mean_split.py"
SPREAD_SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_spread_map.py"
SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_current_family_exact_sigma_target.py"
OUTPUT = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_exact_sigma_target.json"


def test_quark_current_family_exact_sigma_target() -> None:
    subprocess.run([sys.executable, str(SHARED_NORM_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(SPREAD_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(MEAN_SPLIT_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(EXACT_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(SCRIPT)], check=True, cwd=ROOT)
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))

    assert payload["artifact"] == "oph_quark_current_family_exact_sigma_target"
    assert payload["proof_status"] == "closed_current_family_sigma_target"
    assert payload["theorem_scope"] == "current_family_only"
    assert payload["public_promotion_allowed"] is False

    law = payload["fixed_affine_readout_law"]
    target = payload["unique_exact_sigma_target"]
    sigma_seed = float(target["sigma_seed_ud_target"])
    eta = float(target["eta_ud_target"])
    log_u = float(law["log_shift_u"])
    log_d = float(law["log_shift_d"])
    a_ud = float(law["A_ud"])
    b_ud = float(law["B_ud"])

    assert math.isclose(log_u, -(a_ud * sigma_seed - b_ud * eta), rel_tol=0.0, abs_tol=1e-15)
    assert math.isclose(log_d, -(a_ud * sigma_seed + b_ud * eta), rel_tol=0.0, abs_tol=1e-15)

    sigma_u = float(target["sigma_u_target"])
    sigma_d = float(target["sigma_d_target"])
    assert math.isclose(sigma_u, sigma_seed + eta, rel_tol=0.0, abs_tol=1e-15)
    assert math.isclose(sigma_d, sigma_seed - eta, rel_tol=0.0, abs_tol=1e-15)
