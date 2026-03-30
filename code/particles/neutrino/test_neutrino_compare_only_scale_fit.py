#!/usr/bin/env python3
"""Validate the compare-only neutrino single-scale fit surface."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "neutrino" / "derive_neutrino_compare_only_scale_fit.py"
REPAIR_JSON = ROOT / "particles" / "runs" / "neutrino" / "neutrino_weighted_cycle_repair.json"


def test_compare_only_fit_records_single_scale_central_value_mismatch() -> None:
    with tempfile.TemporaryDirectory(prefix="oph_neutrino_fit_") as tmpdir:
        out = pathlib.Path(tmpdir) / "fit.json"
        subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--repair",
                str(REPAIR_JSON),
                "--output",
                str(out),
            ],
            check=True,
            cwd=ROOT,
        )
        payload = json.loads(out.read_text(encoding="utf-8"))
        assert payload["artifact"] == "oph_neutrino_compare_only_scale_fit"
        assert payload["status"] == "compare_only"
        assert payload["exact_central_match_possible_with_single_lambda_nu"] is False
        mismatch = payload["central_ratio_mismatch"]
        assert abs(mismatch["predicted_ratio_21_over_32"] - 0.030721110097966534) < 1.0e-15
        assert abs(mismatch["reference_ratio_21_over_32"] - 0.030721903199343724) < 1.0e-15
        assert abs(mismatch["relative_difference"] + 2.5815502771561345e-05) < 1.0e-15
        weighted = payload["fits"]["weighted_least_squares"]
        assert abs(weighted["lambda_nu"] - 1.7239045130315727) < 1.0e-12
        assert abs(weighted["delta_m_sq_eV2"]["21"] - 7.489824104866108e-05) < 1.0e-15
        assert abs(weighted["delta_m_sq_eV2"]["32"] - 0.0024380056843589996) < 1.0e-15
        assert abs(weighted["residual_sigma"]["21"] + 9.020263276517979e-04) < 1.0e-12
        assert abs(weighted["residual_sigma"]["32"] - 2.8421794998928524e-04) < 1.0e-12
