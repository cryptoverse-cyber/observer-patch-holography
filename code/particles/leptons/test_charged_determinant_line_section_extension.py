#!/usr/bin/env python3
"""Guard the charged determinant-line section extension scaffold."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "particles" / "runs" / "leptons" / "charged_determinant_line_section_extension.json"


def test_determinant_line_extension_contract() -> None:
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert payload["artifact"] == "oph_charged_determinant_line_section_extension"
    assert payload["status"] == "minimal_constructive_extension"
    assert payload["public_promotion_allowed"] is False
    assert payload["exact_missing_object"] == "charged_determinant_line_section"
    assert payload["upstream_prerequisites"]["promotion_theorem"] == "oph_generation_bundle_branch_generator_splitting"
    assert payload["section_contract"]["charged_anchor_readout"] == "A_ch = (1/3) * s_det(det Y_e)"
    assert payload["canonical_formula_on_fill"]["A_ch"] == "(1/3) * log(det(Y_e))"
