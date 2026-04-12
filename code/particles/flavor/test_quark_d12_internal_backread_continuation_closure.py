#!/usr/bin/env python3
"""Validate the D12 quark internal backread continuation sidecar."""

from __future__ import annotations

import json
import math
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
SELECTOR_SCRIPT = ROOT / "particles" / "flavor" / "derive_light_quark_isospin_overlap_defect_selector_law.py"
MASS_RAY_SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_d12_mass_ray.py"
SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_d12_internal_backread_continuation_closure.py"
OUTPUT = ROOT / "particles" / "runs" / "flavor" / "quark_d12_internal_backread_continuation_closure.json"


def test_quark_d12_internal_backread_sidecar_closes_mass_side_without_moving_public_frontier() -> None:
    subprocess.run([sys.executable, str(SELECTOR_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(MASS_RAY_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(SCRIPT)], check=True, cwd=ROOT)

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert payload["artifact"] == "oph_quark_d12_internal_backread_continuation_closure"
    assert payload["proof_status"] == "internal_backread_mass_side_continuation_closed"
    assert payload["scope"] == "D12_continuation_internal_backread_only"
    assert payload["public_promotion_allowed"] is False
    assert payload["changes_public_theorem_frontier"] is False
    assert payload["public_theorem_frontier_still"]["emitted_ray_packaging"] == "quark_d12_t1_value_law"
    assert payload["broader_physical_residual"] == "branch_change_to_physical_ckm_shell"
    checks = payload["consistency_checks"]
    assert math.isclose(checks["delta_minus_t1_over_5"], 0.0, abs_tol=1.0e-15)
    assert math.isclose(checks["eta_minus_formula"], 0.0, abs_tol=1.0e-15)
    assert math.isclose(checks["kappa_minus_formula"], 0.0, abs_tol=1.0e-15)
    source = payload["closed_source_side_package"]
    assert math.isclose(source["beta_u_diag_B_source"], -source["beta_d_diag_B_source"], rel_tol=0.0, abs_tol=1.0e-15)
    assert source["source_readback_u_log_per_side"][1] == 0.0
    assert source["source_readback_d_log_per_side"][1] == 0.0
    assert "weighted transport tau_u depends on the chosen sigma branch" in source["tau_u_log_per_side_note"]
    weighted = payload["closed_weighted_transport_by_sigma_branch"]
    main_branch = weighted["main_builder_sigma_pair"]
    edge_branch = weighted["edge_statistics_bridge_sigma_pair"]
    assert main_branch["provider_artifact"] == "oph_family_excitation_spread_map"
    assert edge_branch["provider_artifact"] == "oph_quark_edge_statistics_spread_candidate"
    assert math.isclose(main_branch["tau_sum_half_delta_identity"], 0.0, abs_tol=1.0e-15)
    assert math.isclose(edge_branch["tau_sum_half_delta_identity"], 0.0, abs_tol=1.0e-15)
