#!/usr/bin/env python3
"""Tests for the current-family transport-frame sector-attached lift artifact."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from derive_quark_current_family_transport_frame_sector_attached_lift import build_artifact


ROOT = Path(__file__).resolve().parents[2]
LINE_LIFT_JSON = ROOT / "particles" / "runs" / "flavor" / "overlap_edge_line_lift.json"
TRANSPORT_FRAME_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_transport_frame_diagnostic_orbit.json"
SIGMA_TARGET_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_exact_sigma_target.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _decode(matrix: dict) -> np.ndarray:
    return np.asarray(matrix["real"], dtype=float) + 1j * np.asarray(matrix["imag"], dtype=float)


def test_transport_frame_sector_attached_lift_closes_current_family_surface() -> None:
    payload = build_artifact(_load(LINE_LIFT_JSON), _load(TRANSPORT_FRAME_JSON), _load(SIGMA_TARGET_JSON))

    assert payload["proof_status"] == "closed_current_family_sector_attached_transport_frame_lift"
    assert payload["theorem_scope"] == "current_family_common_refinement_transport_frame_only"
    assert payload["section_property"]["pi_of_emitted_element_equals_frame_class"] is True

    u_u = _decode(payload["emitted_sigma_ud_phys_element"]["U_u_left"])
    u_d = _decode(payload["emitted_sigma_ud_phys_element"]["U_d_left"])
    v_ckm = _decode(payload["emitted_sigma_ud_phys_element"]["V_CKM"])

    assert np.linalg.norm(u_u.conj().T @ u_u - np.eye(3), ord="fro") < 1.0e-10
    assert np.linalg.norm(u_d.conj().T @ u_d - np.eye(3), ord="fro") < 1.0e-10
    assert np.linalg.norm(u_u.conj().T @ u_d - v_ckm, ord="fro") < 1.0e-10
    assert payload["common_refinement_frame_class"]["matches_transport_frame_diagnostic_fro_residual"] < 1.0e-10

