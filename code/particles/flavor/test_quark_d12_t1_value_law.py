#!/usr/bin/env python3
"""Validate the reduced D12 quark t1 value-law artifact."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
OVERLAP_SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_d12_overlap_transport_law.py"
MASS_RAY_SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_d12_mass_ray.py"
SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_d12_t1_value_law.py"
OUTPUT = ROOT / "particles" / "runs" / "flavor" / "quark_d12_t1_value_law.json"


def main() -> int:
    subprocess.run([sys.executable, str(OVERLAP_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(MASS_RAY_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(SCRIPT)], check=True, cwd=ROOT)

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    if payload.get("artifact") != "oph_quark_d12_t1_value_law":
        print("wrong quark D12 t1 value-law artifact id", file=sys.stderr)
        return 1
    if payload.get("proof_status") != "closed_mass_ray_one_scalar_value_law":
        print("unexpected quark D12 t1 value-law proof status", file=sys.stderr)
        return 1
    if payload.get("public_promotion_allowed") is not True:
        print("quark D12 t1 value-law should now be promotable on the code surface", file=sys.stderr)
        return 1
    if payload.get("exact_missing_object") is not None:
        print("quark D12 t1 value-law should no longer record itself as missing", file=sys.stderr)
        return 1
    forced = payload["forced_source_payload_after_t1"]
    if forced["beta_u_diag_B_source"] != "t1 / 10" or forced["beta_d_diag_B_source"] != "-t1 / 10":
        print("t1 law should force the pure-B source scalar pair exactly", file=sys.stderr)
        return 1
    reduction = payload["transport_side_reduction"]
    if reduction["status"] != "closed_given_fixed_sigma_branch":
        print("transport side should be reduced to a closed law once sigma branch is fixed", file=sys.stderr)
        return 1
    if reduction["weighted_transport_formulas_after_t1"]["tau_u_log_per_side"] != "sigma_d_total_log_per_side * t1 / (10 * (sigma_u_total_log_per_side + sigma_d_total_log_per_side))":
        print("unexpected tau_u formula after t1 reduction", file=sys.stderr)
        return 1
    if reduction["exact_gap_after_transport_reduction"] != "supported_sigma_branch_emission":
        print("remaining reduced gap after transport closure should be the sigma branch emission", file=sys.stderr)
        return 1
    route = payload["candidate_public_construction_route"]
    if route["candidate_scalar_identities"] != [
        "log(c_d / c_u) = (6/5) * t1",
        "t1 = 5 * Delta_ud_overlap = (5/6) * log(c_d / c_u)",
    ]:
        print("unexpected candidate scalar route identities", file=sys.stderr)
        return 1
    if route["status"] != "closed_theorem_internalized":
        print("candidate route should now be marked internalized", file=sys.stderr)
        return 1
    frontier = payload["current_public_yukawa_frontier"]
    if frontier["remaining_exact_blocker_set_if_this_branch_is_used"] != []:
        print("public current-family Yukawa frontier should now be closed on the main sigma branch", file=sys.stderr)
        return 1
    if frontier["target_1_status"] != "closed":
        print("target 1 should now be marked closed", file=sys.stderr)
        return 1
    if frontier["equivalent_ray_coordinate_presentation"] != "quark_d12_t1_value_law":
        print("t1 scaffold should still identify itself as the equivalent ray-coordinate presentation", file=sys.stderr)
        return 1
    if frontier["theorem_grade_sigma_branch_status"] != "closed":
        print("main-builder sigma branch should already be theorem-grade", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
