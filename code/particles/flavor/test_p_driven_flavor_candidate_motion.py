#!/usr/bin/env python3
"""Validate the off-canonical P-driven flavor candidate motion surface."""

from __future__ import annotations

import json
import math
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
CALIBRATION_DIR = ROOT / "particles" / "calibration"
FLAVOR_DIR = ROOT / "particles" / "flavor"

D10_FAMILY_SCRIPT = CALIBRATION_DIR / "derive_d10_ew_observable_family.py"
D10_SOURCE_PAIR_SCRIPT = CALIBRATION_DIR / "derive_d10_ew_source_transport_pair.py"
KERNEL_SCRIPT = FLAVOR_DIR / "derive_family_transport_kernel.py"
GENERATOR_SCRIPT = FLAVOR_DIR / "derive_generation_bundle_branch_generator.py"
LINE_LIFT_SCRIPT = FLAVOR_DIR / "derive_overlap_edge_line_lift.py"
COCYCLE_SCRIPT = FLAVOR_DIR / "derive_overlap_edge_transport_cocycle.py"
OBSERVABLE_SCRIPT = FLAVOR_DIR / "derive_overlap_flavor_observable.py"
SECTOR_PUSHFORWARD_SCRIPT = FLAVOR_DIR / "derive_sector_transport_pushforward.py"
CHARGED_BUDGET_SCRIPT = FLAVOR_DIR / "derive_charged_budget_pushforward.py"
TENSORS_SCRIPT = FLAVOR_DIR / "derive_suppression_phase_tensors.py"
ODD_RESPONSE_SCRIPT = FLAVOR_DIR / "derive_quark_odd_response_law.py"
FAMILY_EXCITATION_SCRIPT = FLAVOR_DIR / "derive_family_excitation_evaluator.py"
EDGE_STATS_SCRIPT = FLAVOR_DIR / "derive_quark_edge_statistics_spread_candidate.py"
SPREAD_MAP_SCRIPT = FLAVOR_DIR / "derive_quark_spread_map.py"
MASS_SURFACE_SCRIPT = FLAVOR_DIR / "derive_quark_p_driven_candidate_mass_surface.py"

EXACT_READOUT_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_exact_readout.json"
EXACT_SIGMA_TARGET_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_exact_sigma_target.json"
BASELINE_SPREAD_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_spread_map.json"


def _run(script: pathlib.Path, *args: str) -> None:
    subprocess.run([sys.executable, str(script), *args], check=True, cwd=ROOT)


def _load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _build_candidate_surface(tmp_path: pathlib.Path, p_value: float) -> tuple[dict, dict, dict]:
    d10_family = tmp_path / f"d10_family_{p_value:.5f}.json"
    d10_source = tmp_path / f"d10_source_{p_value:.5f}.json"
    kernel = tmp_path / f"kernel_{p_value:.5f}.json"
    generator = tmp_path / f"generator_{p_value:.5f}.json"
    line_lift = tmp_path / f"line_lift_{p_value:.5f}.json"
    cocycle = tmp_path / f"cocycle_{p_value:.5f}.json"
    observable = tmp_path / f"observable_{p_value:.5f}.json"
    sector_pushforward = tmp_path / f"sector_pushforward_{p_value:.5f}.json"
    charged_budget = tmp_path / f"charged_budget_{p_value:.5f}.json"
    tensors = tmp_path / f"tensors_{p_value:.5f}.json"
    odd_response = tmp_path / f"odd_response_{p_value:.5f}.json"
    family_excitation = tmp_path / f"family_excitation_{p_value:.5f}.json"
    edge_stats = tmp_path / f"edge_stats_{p_value:.5f}.json"
    spread_map = tmp_path / f"spread_{p_value:.5f}.json"
    mass_surface = tmp_path / f"mass_surface_{p_value:.5f}.json"

    _run(D10_FAMILY_SCRIPT, "--p", f"{p_value:.12f}", "--output", str(d10_family))
    _run(D10_SOURCE_PAIR_SCRIPT, "--input", str(d10_family), "--output", str(d10_source))
    _run(
        KERNEL_SCRIPT,
        "--mode",
        "p_driven_candidate",
        "--d10-family",
        str(d10_family),
        "--d10-source-pair",
        str(d10_source),
        "--output",
        str(kernel),
    )
    _run(GENERATOR_SCRIPT, "--input", str(kernel), "--output", str(generator))
    _run(LINE_LIFT_SCRIPT, "--input", str(kernel), "--generator", str(generator), "--output", str(line_lift))
    _run(COCYCLE_SCRIPT, "--input", str(kernel), "--line-lift", str(line_lift), "--output", str(cocycle))
    _run(OBSERVABLE_SCRIPT, "--input", str(kernel), "--cocycle", str(cocycle), "--output", str(observable))
    _run(SECTOR_PUSHFORWARD_SCRIPT, "--input", str(observable), "--output", str(sector_pushforward))
    _run(CHARGED_BUDGET_SCRIPT, "--input", str(sector_pushforward), "--output", str(charged_budget))
    _run(TENSORS_SCRIPT, "--input", str(sector_pushforward), "--output", str(tensors))
    _run(
        ODD_RESPONSE_SCRIPT,
        "--observable",
        str(observable),
        "--charged-budget",
        str(charged_budget),
        "--tensors",
        str(tensors),
        "--output",
        str(odd_response),
    )
    _run(GENERATOR_SCRIPT, "--input", str(kernel), "--output", str(generator))
    _run(FAMILY_EXCITATION_SCRIPT, "--generator", str(generator), "--output", str(family_excitation))
    _run(
        EDGE_STATS_SCRIPT,
        "--family",
        str(family_excitation),
        "--odd-response",
        str(odd_response),
        "--cocycle",
        str(cocycle),
        "--spread",
        str(tmp_path / "missing_spread_anchor.json"),
        "--output",
        str(edge_stats),
    )
    _run(
        SPREAD_MAP_SCRIPT,
        "--mode",
        "p_driven_candidate",
        "--input",
        str(family_excitation),
        "--odd-response-law",
        str(odd_response),
        "--sector-mean-split",
        str(tmp_path / "missing_mean_split.json"),
        "--edge-stats-candidate",
        str(edge_stats),
        "--output",
        str(spread_map),
    )
    _run(
        MASS_SURFACE_SCRIPT,
        "--spread-map",
        str(spread_map),
        "--baseline-spread-map",
        str(BASELINE_SPREAD_JSON),
        "--exact-readout",
        str(EXACT_READOUT_JSON),
        "--exact-sigma-target",
        str(EXACT_SIGMA_TARGET_JSON),
        "--output",
        str(mass_surface),
    )
    return _load(kernel), _load(spread_map), _load(mass_surface)


def test_p_driven_flavor_candidate_moves_off_canonical_but_recovers_exact_default_anchor(tmp_path: pathlib.Path) -> None:
    default_kernel, default_spread, default_mass_surface = _build_candidate_surface(tmp_path, 1.63094)
    moved_kernel, moved_spread, moved_mass_surface = _build_candidate_surface(tmp_path, 1.76094)
    exact_readout = _load(EXACT_READOUT_JSON)
    exact_sigma_target = _load(EXACT_SIGMA_TARGET_JSON)

    assert default_kernel["status"] == "p_driven_default_universe_anchor_candidate"
    assert default_kernel["proof_status"] == "candidate_only"
    assert default_spread["spread_emitter_status"] == "candidate_default_universe_exact_anchor"
    assert default_spread["sigma_source_kind"] == "p_driven_edge_statistics_default_universe_anchor_candidate"

    target = exact_sigma_target["unique_exact_sigma_target"]
    assert math.isclose(
        default_spread["sigma_u_total_log_per_side"],
        target["sigma_u_target"],
        rel_tol=0.0,
        abs_tol=1.0e-12,
    )
    assert math.isclose(
        default_spread["sigma_d_total_log_per_side"],
        target["sigma_d_target"],
        rel_tol=0.0,
        abs_tol=1.0e-12,
    )

    default_u = [row["mass"] for row in default_mass_surface["current_candidate_masses"]["up_sector"]]
    default_d = [row["mass"] for row in default_mass_surface["current_candidate_masses"]["down_sector"]]
    exact_u = [float(value) for value in exact_readout["predicted_singular_values_u"]]
    exact_d = [float(value) for value in exact_readout["predicted_singular_values_d"]]
    for observed, expected in zip(default_u, exact_u, strict=True):
        assert math.isclose(observed, expected, rel_tol=0.0, abs_tol=1.0e-10)
    for observed, expected in zip(default_d, exact_d, strict=True):
        assert math.isclose(observed, expected, rel_tol=0.0, abs_tol=1.0e-10)

    assert moved_spread["sigma_u_total_log_per_side"] != default_spread["sigma_u_total_log_per_side"]
    assert moved_spread["sigma_d_total_log_per_side"] != default_spread["sigma_d_total_log_per_side"]

    moved_u = [row["mass"] for row in moved_mass_surface["current_candidate_masses"]["up_sector"]]
    moved_d = [row["mass"] for row in moved_mass_surface["current_candidate_masses"]["down_sector"]]
    assert any(not math.isclose(left, right, rel_tol=0.0, abs_tol=1.0e-10) for left, right in zip(moved_u, exact_u, strict=True))
    assert any(not math.isclose(left, right, rel_tol=0.0, abs_tol=1.0e-10) for left, right in zip(moved_d, exact_d, strict=True))
