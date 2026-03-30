#!/usr/bin/env python3
"""Validate the charged central-split transfer extension artifact."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "flavor" / "derive_charged_central_split_transfer_extension.py"
OUTPUT = ROOT / "particles" / "runs" / "flavor" / "charged_central_split_transfer_extension.json"


def test_charged_central_split_transfer_extension_exposes_minimal_route() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], check=True, cwd=ROOT)
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert payload["artifact"] == "oph_charged_central_split_transfer_extension"
    assert payload["status"] == "proved_as_minimal_extension"
    assert payload["theorem"]["id"] == "central_split_quadratic_commutator_transfer"
    assert payload["remaining_object_after_extension"]["id"] == "charged_absolute_anchor_A_ch"
    assert payload["local_numeric_promotion_test"]["sufficient_uniform_constant_bound"] > 100.0
