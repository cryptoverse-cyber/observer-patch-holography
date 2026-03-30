#!/usr/bin/env python3
"""Validate the local quark basis-orbit diagnostic."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "flavor" / "enumerate_quark_local_basis_orbit_diagnostic.py"
OUTPUT = ROOT / "particles" / "runs" / "flavor" / "quark_local_basis_orbit_diagnostic.json"


def test_quark_local_basis_orbit_diagnostic_exposes_nine_basis_choices() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], check=True, cwd=ROOT)
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert payload["artifact"] == "oph_quark_local_basis_orbit_diagnostic"
    assert payload["scope"] == "D12_current_reference_local_basis_only"
    assert len(payload["elements"]) == 9
    admissible = [item for item in payload["elements"] if item["physical_admissible"]]
    assert len(admissible) == 1
    assert admissible[0]["basis_u"] == "L"
    assert admissible[0]["basis_d"] == "L"
    assert payload["best_nonphysical_candidate"] is not None
    assert payload["best_nonphysical_candidate"]["physical_admissible"] is False

