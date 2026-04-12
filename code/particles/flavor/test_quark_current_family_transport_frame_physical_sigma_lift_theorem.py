#!/usr/bin/env python3
"""Tests for the restricted-carrier physical sigma-lift theorem artifact."""

from __future__ import annotations

import json
from pathlib import Path

from derive_quark_current_family_transport_frame_physical_sigma_lift_theorem import build_artifact


ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / "particles" / "runs" / "flavor"


def test_current_family_transport_frame_physical_sigma_lift_theorem_closes() -> None:
    lift = json.loads((RUNS / "quark_current_family_transport_frame_sector_attached_lift.json").read_text(encoding="utf-8"))
    payload = build_artifact(lift)

    assert payload["artifact"] == "oph_quark_current_family_transport_frame_physical_sigma_lift_theorem"
    assert payload["proof_status"] == "closed_current_family_transport_frame_physical_sigma_lift_theorem"
    assert payload["corresponds_to_global_contract"]["id"] == "quark_physical_sigma_ud_lift"
    assert payload["theorem_scope"] == "current_family_common_refinement_transport_frame_only"
    assert payload["emitted_sigma_ud_phys_element"]["sigma_id"] == "sigma_phys_transport_frame_current_family"

