#!/usr/bin/env python3
"""Tests for the restricted-carrier quark D12 value package artifact."""

from __future__ import annotations

import json
from pathlib import Path

from derive_quark_current_family_transport_frame_d12_value_package import build_artifact


ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / "particles" / "runs" / "flavor"


def test_current_family_transport_frame_d12_value_package_closes() -> None:
    light_ratio = json.loads((RUNS / "quark_current_family_transport_frame_light_ratio_theorem.json").read_text(encoding="utf-8"))
    spread_map = json.loads((RUNS / "quark_spread_map.json").read_text(encoding="utf-8"))
    overlap_law = json.loads((RUNS / "quark_d12_overlap_transport_law.json").read_text(encoding="utf-8"))
    mass_ray = json.loads((RUNS / "quark_d12_mass_ray.json").read_text(encoding="utf-8"))
    payload = build_artifact(light_ratio, spread_map, overlap_law, mass_ray)

    assert payload["artifact"] == "oph_quark_current_family_transport_frame_d12_value_package"
    assert payload["proof_status"] == "closed_current_family_transport_frame_d12_value_package"
    assert payload["theorem_scope"] == "current_family_common_refinement_transport_frame_only"
    scalars = payload["closed_d12_scalars"]
    assert abs(float(scalars["Delta_ud_overlap"]) - 0.1295757145033233) < 1.0e-12
    assert abs(float(scalars["t1"]) - 0.6478785725166165) < 1.0e-12

