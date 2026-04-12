#!/usr/bin/env python3
"""Verify the exported flavor dictionary preserves the quark edge-statistics bridge."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
SPREAD_SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_spread_map.py"
DESCENT_SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_sector_descent.py"
FORWARD_SCRIPT = ROOT / "particles" / "flavor" / "build_forward_yukawas.py"
EXPORT_SCRIPT = ROOT / "particles" / "flavor" / "export_flavor_dictionary_artifact.py"
DESCENT_OUTPUT = ROOT / "particles" / "runs" / "flavor" / "quark_sector_descent.json"
FORWARD_OUTPUT = ROOT / "particles" / "runs" / "flavor" / "forward_yukawas.json"
SPREAD_OUTPUT = ROOT / "particles" / "runs" / "flavor" / "quark_spread_map.json"
DICTIONARY_OUTPUT = ROOT / "particles" / "runs" / "flavor" / "flavor_dictionary_artifact.json"


def test_flavor_dictionary_preserves_constructive_quark_edge_bridge() -> None:
    subprocess.run([sys.executable, str(SPREAD_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(DESCENT_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(FORWARD_SCRIPT), "--input", str(DESCENT_OUTPUT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(EXPORT_SCRIPT)], check=True, cwd=ROOT)

    spread = json.loads(SPREAD_OUTPUT.read_text(encoding="utf-8"))
    forward = json.loads(FORWARD_OUTPUT.read_text(encoding="utf-8"))
    dictionary = json.loads(DICTIONARY_OUTPUT.read_text(encoding="utf-8"))

    bridge_sigmas = spread["metadata"]["constructive_edge_statistics_bridge_candidate_sigmas"]

    assert forward["constructive_edge_statistics_bridge_artifact"] == "oph_quark_edge_statistics_spread_candidate"
    assert forward["constructive_edge_statistics_bridge_status"] == "candidate_only"
    assert forward["constructive_edge_statistics_bridge_candidate_sigmas"] == bridge_sigmas
    assert forward["spread_sigma_source_kind"] == spread["sigma_source_kind"]
    assert forward["spread_sigma_u_total_log_per_side"] == spread["sigma_u_total_log_per_side"]
    assert forward["spread_sigma_d_total_log_per_side"] == spread["sigma_d_total_log_per_side"]

    assert dictionary["quark_edge_statistics_bridge_artifact"] == "oph_quark_edge_statistics_spread_candidate"
    assert dictionary["quark_edge_statistics_bridge_status"] == "candidate_only"
    assert dictionary["quark_edge_statistics_bridge_candidate_sigmas"] == bridge_sigmas
    assert dictionary["quark_spread_sigma_source_kind"] == spread["sigma_source_kind"]
    assert dictionary["quark_spread_sigma_u_total_log_per_side"] == spread["sigma_u_total_log_per_side"]
    assert dictionary["quark_spread_sigma_d_total_log_per_side"] == spread["sigma_d_total_log_per_side"]
    assert dictionary["quark_even_excitation_source_artifact"] == spread["artifact"]
    assert dictionary["quark_even_excitation_source_status"] == spread["spread_emitter_status"]
