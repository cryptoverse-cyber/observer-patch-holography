#!/usr/bin/env python3
"""Validate the quark absolute-readout algebraic collapse artifact."""

from __future__ import annotations

import json
import math
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_absolute_readout_algebraic_collapse.py"
OUTPUT = ROOT / "particles" / "runs" / "flavor" / "quark_absolute_readout_algebraic_collapse.json"


def test_quark_absolute_readout_algebraic_collapse() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], check=True, cwd=ROOT)
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))

    assert payload["artifact"] == "oph_quark_absolute_readout_algebraic_collapse"
    assert payload["proof_status"] == "closed_algebraic_collapse_given_theorem_grade_sigma_datum"
    assert payload["theorem_scope"] == "conditional_on_strengthened_physical_sigma_lift"
    assert payload["public_promotion_allowed"] is False
    assert payload["conditional_collapse_route"]["collapsed_theorem"] == "quark_absolute_sector_readout_theorem"

    law = payload["fixed_affine_mean_law"]
    sigma = payload["exact_current_family_sigma_specialization"]
    a_ud = float(law["A_ud"])
    b_ud = float(law["B_ud"])
    g_ch = float(law["g_ch"])
    sigma_seed = float(sigma["sigma_seed_ud_target"])
    eta = float(sigma["eta_ud_target"])
    g_u = float(sigma["g_u_forced"])
    g_d = float(sigma["g_d_forced"])

    assert math.isclose(g_u, g_ch * math.exp(-(a_ud * sigma_seed - b_ud * eta)), rel_tol=0.0, abs_tol=1e-15)
    assert math.isclose(g_d, g_ch * math.exp(-(a_ud * sigma_seed + b_ud * eta)), rel_tol=0.0, abs_tol=1e-15)
    assert payload["exact_current_family_pdg_consequence"]["artifact"] == "oph_quark_current_family_exact_pdg_theorem"
