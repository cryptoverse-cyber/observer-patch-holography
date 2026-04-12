#!/usr/bin/env python3
"""Validate the synthesized quark target-free bridge theorem package."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
TARGET_SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_d12_current_family_target_anchored_value_package.py"
SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_target_free_bridge_theorem.py"
OUTPUT = ROOT / "particles" / "runs" / "flavor" / "quark_target_free_bridge_theorem.json"


def test_quark_target_free_bridge_theorem_package() -> None:
    subprocess.run([sys.executable, str(TARGET_SCRIPT)], check=True)
    subprocess.run([sys.executable, str(SCRIPT)], check=True)
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))

    assert payload["artifact"] == "oph_quark_target_free_bridge_theorem"
    assert payload["proof_status"] == "closed_target_free_bridge_theorem_internalized"
    assert payload["public_promotion_allowed"] is True
    assert payload["bridge_closure_status"] == "internalized_on_code_surface"
    assert payload["theorem_ids"] == [
        "light_quark_overlap_defect_value_law",
        "quark_d12_t1_value_law",
    ]
    assert "Delta_ud_overlap = (1/6) * log(c_d / c_u)" in payload["principal_theorem_statement"]
    assert payload["proof_skeleton"][0]["statement"].endswith("log(y_d / y_u) = log(c_d / c_u).")
    assert "(1/6) * log(y_d / y_u)" in payload["proof_skeleton"][1]["statement"]
    assert payload["single_bridge_gap_to_internalize"] is None
    target = payload["computed_current_family_target_check"]
    assert target is not None
    assert float(target["t1"]) > 0.0
