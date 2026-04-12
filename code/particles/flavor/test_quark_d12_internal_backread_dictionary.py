#!/usr/bin/env python3
"""Validate the continuation-only D12 internal-backread quark dictionary sidecars."""

from __future__ import annotations

import json
import math
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
OVERLAP_LAW_SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_d12_overlap_transport_law.py"
SOURCE_PAYLOAD_SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_d12_internal_backread_source_payload.py"
DICTIONARY_SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_d12_internal_backread_yukawa_dictionary.py"
SOURCE_PAYLOAD_OUTPUT = ROOT / "particles" / "runs" / "flavor" / "quark_d12_internal_backread_source_payload.json"
DICTIONARY_OUTPUT = ROOT / "particles" / "runs" / "flavor" / "quark_d12_internal_backread_yukawa_dictionary.json"


def main() -> int:
    subprocess.run([sys.executable, str(OVERLAP_LAW_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(SOURCE_PAYLOAD_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(DICTIONARY_SCRIPT)], check=True, cwd=ROOT)

    source_payload = json.loads(SOURCE_PAYLOAD_OUTPUT.read_text(encoding="utf-8"))
    dictionary = json.loads(DICTIONARY_OUTPUT.read_text(encoding="utf-8"))

    if source_payload.get("artifact") != "oph_quark_d12_internal_backread_source_payload":
        print("wrong D12 internal-backread source payload artifact id", file=sys.stderr)
        return 1
    if source_payload.get("proof_status") != "internal_backread_source_payload_emitted":
        print("internal-backread source payload should be emitted on the sidecar surface", file=sys.stderr)
        return 1
    if not math.isclose(
        source_payload["J_B_source_u"],
        (source_payload["source_readback_u_log_per_side"][2] - source_payload["source_readback_u_log_per_side"][0]) / 2.0,
        rel_tol=0.0,
        abs_tol=1.0e-15,
    ):
        print("J_B_source_u should be the endpoint readback of the emitted pure-B payload", file=sys.stderr)
        return 1
    if not math.isclose(source_payload["beta_u_diag_B_source"], -source_payload["beta_d_diag_B_source"], rel_tol=0.0, abs_tol=1.0e-15):
        print("odd budget neutrality should hold on the emitted source payload", file=sys.stderr)
        return 1

    if dictionary.get("artifact") != "oph_quark_d12_internal_backread_yukawa_dictionary":
        print("wrong D12 internal-backread Yukawa dictionary artifact id", file=sys.stderr)
        return 1
    if dictionary.get("scope") != "D12_continuation_internal_backread_only":
        print("dictionary sidecar should remain continuation-only", file=sys.stderr)
        return 1
    if dictionary["odd_source_payload"]["J_B_source_u"] is None or dictionary["odd_source_payload"]["J_B_source_d"] is None:
        print("dictionary sidecar should carry the emitted odd source scalar pair", file=sys.stderr)
        return 1
    transport = dictionary["odd_transport_lift"]
    if transport["tau_formula_kind"] != "explicit_edge_branch_overlap_law_internal_backread_realization":
        print("dictionary sidecar should consume the explicit edge-branch overlap law when available", file=sys.stderr)
        return 1
    if transport["consumed_overlap_law_artifact"] != "oph_quark_d12_overlap_transport_law":
        print("dictionary sidecar should record the consumed overlap-law artifact", file=sys.stderr)
        return 1
    if abs(transport["tau_sum_half_delta_identity"]) > 1.0e-12:
        print("weighted tau pair should satisfy tau_u + tau_d = Delta/2", file=sys.stderr)
        return 1
    if abs(transport["tau_ratio_minus_sigma_ratio"]) > 1.0e-12:
        print("weighted tau pair should preserve the sigma_d/tau_u ratio identity", file=sys.stderr)
        return 1
    forward = dictionary["forward_surface"]
    if any(value <= 0.0 for value in forward["singular_values_u"] + forward["singular_values_d"]):
        print("dictionary sidecar should emit positive singular values", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
