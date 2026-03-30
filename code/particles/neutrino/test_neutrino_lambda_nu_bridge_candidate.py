#!/usr/bin/env python3
"""Guard the neutrino lambda_nu bridge candidate scaffold."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "neutrino" / "derive_neutrino_lambda_nu_bridge_candidate.py"
OUTPUT = ROOT / "particles" / "runs" / "neutrino" / "neutrino_lambda_nu_bridge_candidate.json"


def test_neutrino_lambda_nu_bridge_candidate() -> None:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--output", str(OUTPUT)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "saved:" in completed.stdout
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert payload["artifact"] == "oph_neutrino_lambda_nu_bridge_candidate"
    assert payload["exact_missing_interface_object"] == "oph_majorana_overlap_defect_scalar_evaluator"
    assert payload["bridge_ansatz"] == "lambda_nu = m_star_eV * F_nu"
    assert payload["compare_only_bridge_factor"]["F_nu_star"] > 1.0
    closed_form = payload["target_free_closed_form_candidates"][0]
    assert closed_form["name"] == "gamma_over_sqrt_ratio_hat"
    assert abs(closed_form["residual_sigma"]["21"]) < 0.1
    assert abs(closed_form["residual_sigma"]["32"]) < 0.2
