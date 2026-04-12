#!/usr/bin/env python3
"""Tests for the restricted-carrier quark light-ratio theorem artifact."""

from __future__ import annotations

import json
from pathlib import Path

from derive_quark_current_family_transport_frame_light_ratio_theorem import build_artifact


ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / "particles" / "runs" / "flavor"


def test_current_family_transport_frame_light_ratio_theorem_closes() -> None:
    pdg_completion = json.loads((RUNS / "quark_current_family_transport_frame_exact_pdg_completion.json").read_text(encoding="utf-8"))
    payload = build_artifact(pdg_completion)

    assert payload["artifact"] == "oph_quark_current_family_transport_frame_light_ratio_theorem"
    assert payload["proof_status"] == "closed_current_family_transport_frame_light_ratio_theorem"
    assert payload["theorem_scope"] == "current_family_common_refinement_transport_frame_only"
    assert abs(float(payload["exact_light_data"]["ell_ud"]) - 0.7774542870199399) < 1.0e-12

