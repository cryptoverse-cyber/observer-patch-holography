#!/usr/bin/env python3
"""Guard the UV/BW internalization scaffold."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "particles" / "runs" / "uv" / "bw_internalization_scaffold.json"


def test_bw_internalization_scaffold_contract() -> None:
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert payload["artifact"] == "oph_uv_bw_internalization_scaffold"
    assert payload["status"] == "minimal_constructive_extension"
    assert payload["public_promotion_allowed"] is False
    assert payload["extension_kind"] == "scaling_limit_cap_pair_plus_ordered_cut_pair_rigidity"
    assert payload["solver_spec"]["output_certificate"]["typeI_required"] is False
    boundary = payload["public_status_boundary"]
    assert boundary["remaining_object"] == "canonical_scaling_cap_pair_realization_from_transported_cap_marginals"
    assert boundary["follow_on_object"] == "independent_bw_rigidity_on_realized_limit"
    rigidity = boundary["symbolic_ordered_cut_pair_rigidity_test"]
    assert rigidity["status"] == "pass"
    assert rigidity["solution_dimension"] == 1
    assert rigidity["surviving_generator_half_line"] == "2*u"
