#!/usr/bin/env python3
"""Emit the strengthened restricted-carrier physical sigma-lift theorem for the quark lane."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PHYSICAL_SIGMA_THEOREM_JSON = (
    ROOT / "particles" / "runs" / "flavor" / "quark_current_family_transport_frame_physical_sigma_lift_theorem.json"
)
SIGMA_TARGET_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_exact_sigma_target.json"
DEFAULT_OUT = (
    ROOT / "particles" / "runs" / "flavor" / "quark_current_family_transport_frame_strengthened_physical_sigma_lift_theorem.json"
)


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_artifact(physical_sigma_theorem: dict, sigma_target: dict) -> dict:
    emitted = dict(physical_sigma_theorem["emitted_sigma_ud_phys_element"])
    target = dict(sigma_target["unique_exact_sigma_target"])
    return {
        "artifact": "oph_quark_current_family_transport_frame_strengthened_physical_sigma_lift_theorem",
        "generated_utc": _timestamp(),
        "proof_status": "closed_current_family_transport_frame_strengthened_physical_sigma_lift_theorem",
        "theorem_scope": physical_sigma_theorem["theorem_scope"],
        "public_promotion_allowed": False,
        "compressed_global_contract": {
            "id": "strengthened_quark_physical_sigma_ud_lift",
            "role": "one_nonalgebraic_public_burden_after_absolute_collapse",
            "carrier_restriction": physical_sigma_theorem["theorem_scope"],
        },
        "supporting_artifacts": {
            "restricted_physical_sigma_lift_theorem": physical_sigma_theorem["artifact"],
            "exact_sigma_target": sigma_target["artifact"],
        },
        "theorem_statement": (
            "On the explicit current-family common-refinement transport-frame carrier, the same-label line-lift "
            "transport data determine a sector-attached element of Sigma_ud^phys over the frame class [F0^dagger F1], "
            "and the fixed affine readout law attaches the unique exact sigma target "
            "(sigma_seed_ud, eta_ud, sigma_u, sigma_d). Equivalently, the restricted-carrier analogue of the "
            "strengthened quark physical sigma lift is closed on that declared surface."
        ),
        "restricted_sigma_ud_phys_element": emitted,
        "restricted_section_theorem": physical_sigma_theorem["restricted_section_theorem"],
        "common_refinement_frame_class": physical_sigma_theorem["common_refinement_frame_class"],
        "quotient_well_definedness": physical_sigma_theorem["quotient_well_definedness"],
        "theorem_grade_physical_sigma_datum": {
            "sigma_seed_ud": float(target["sigma_seed_ud_target"]),
            "eta_ud": float(target["eta_ud_target"]),
            "sigma_u": float(target["sigma_u_target"]),
            "sigma_d": float(target["sigma_d_target"]),
        },
        "notes": [
            "This theorem merges the restricted-carrier physical sigma lift with the exact current-family sigma target.",
            "It is the local strengthened analogue of the single remaining nonalgebraic public burden after absolute readout collapse.",
            "It does not claim target-free public promotion beyond the declared current-family/common-refinement transport-frame surface.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the strengthened restricted-carrier quark physical sigma-lift theorem artifact.")
    parser.add_argument("--physical-sigma-theorem", default=str(PHYSICAL_SIGMA_THEOREM_JSON))
    parser.add_argument("--sigma-target", default=str(SIGMA_TARGET_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    payload = build_artifact(
        _load_json(Path(args.physical_sigma_theorem)),
        _load_json(Path(args.sigma_target)),
    )
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
