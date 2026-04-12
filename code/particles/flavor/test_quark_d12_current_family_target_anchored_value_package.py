#!/usr/bin/env python3
"""Validate the computed current-family target-anchored D12 value package."""

from __future__ import annotations

import json
import math
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
LIGHT_RATIO_SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_current_family_light_ratio_theorem.py"
SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_d12_current_family_target_anchored_value_package.py"
OUTPUT = ROOT / "particles" / "runs" / "flavor" / "quark_d12_current_family_target_anchored_value_package.json"


def test_current_family_target_anchored_value_package() -> None:
    subprocess.run([sys.executable, str(LIGHT_RATIO_SCRIPT)], check=True)
    subprocess.run([sys.executable, str(SCRIPT)], check=True)
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))

    assert payload["artifact"] == "oph_quark_d12_current_family_target_anchored_value_package"
    assert payload["scope"] == "current_family_only"
    assert payload["public_promotion_allowed"] is False
    assert payload["source_artifacts"]["light_ratio_theorem"] == "oph_quark_current_family_light_ratio_theorem"

    ell = float(payload["target_anchored_inputs"]["ell_ud"])
    delta = float(payload["computed_d12_scalars"]["Delta_ud_overlap"])
    t1 = float(payload["computed_d12_scalars"]["t1"])

    assert math.isclose(delta, ell / 6.0, rel_tol=0.0, abs_tol=1e-15)
    assert math.isclose(t1, 5.0 * delta, rel_tol=0.0, abs_tol=1e-15)
    assert math.isclose(float(payload["computed_d12_scalars"]["ray_modulus"]), t1, rel_tol=0.0, abs_tol=1e-15)
    assert math.isclose(float(payload["forced_source_payload"]["beta_u_diag_B_source"]), t1 / 10.0, rel_tol=0.0, abs_tol=1e-15)
    assert math.isclose(float(payload["forced_source_payload"]["beta_d_diag_B_source"]), -t1 / 10.0, rel_tol=0.0, abs_tol=1e-15)

    transport = payload["transport_on_theorem_grade_sigma_branch"]
    tau_u = float(transport["tau_u_log_per_side"])
    tau_d = float(transport["tau_d_log_per_side"])
    assert math.isclose(tau_u + tau_d, delta / 2.0, rel_tol=0.0, abs_tol=1e-15)
    assert math.isclose(float(transport["tau_u_plus_tau_d"]), delta / 2.0, rel_tol=0.0, abs_tol=1e-15)

    comparison = payload["comparison_to_other_local_d12_packages"]
    assert "sample_same_family_point" in comparison
    assert "difference_vs_sample_same_family_point" in comparison
    assert "internal_backread" in comparison
    assert "difference_vs_internal_backread" in comparison

    theorem_values = payload["computed_candidate_theorem_values"]["quark_d12_t1_value_law"]
    assert math.isclose(float(theorem_values["ell_ud"]), ell, rel_tol=0.0, abs_tol=1e-15)
    assert math.isclose(float(theorem_values["t1"]), t1, rel_tol=0.0, abs_tol=1e-15)
