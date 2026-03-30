#!/usr/bin/env python3
"""Validate the standard-math-fixed neutrino transport-load selector."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "neutrino" / "derive_neutrino_transport_load_segment_selector.py"
COCYCLE = ROOT / "particles" / "runs" / "flavor" / "overlap_edge_transport_cocycle.json"


def test_transport_load_segment_selector_closes_at_midpoint() -> None:
    with tempfile.TemporaryDirectory(prefix="oph_neutrino_load_selector_") as tmpdir:
        out = pathlib.Path(tmpdir) / "selector.json"
        subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--cocycle",
                str(COCYCLE),
                "--output",
                str(out),
            ],
            check=True,
            cwd=ROOT,
        )
        payload = json.loads(out.read_text(encoding="utf-8"))
        assert payload["artifact"] == "oph_neutrino_transport_load_segment_selector"
        assert payload["status"] == "standard_math_fixed_balanced_segment_selector_closed"
        assert payload["closure_scope"] == "standard_math_fixed"
        assert payload["selected_selector"] == "balanced_equals_least_distortion_midpoint"
        assert abs(payload["selected_tau_nu"] - 0.5) < 1.0e-15
        assert abs(payload["selected_D_nu"] - 1.127883690210334) < 1.0e-15
        assert abs(payload["derived_quantities"]["weight_exponent_value"] - 1.395092021318097) < 1.0e-15
