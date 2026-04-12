#!/usr/bin/env python3
"""Emit the restricted-carrier absolute sector-readout theorem for the quark lane."""

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
ABSOLUTE_COLLAPSE_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_absolute_readout_algebraic_collapse.json"
DEFAULT_OUT = (
    ROOT / "particles" / "runs" / "flavor" / "quark_current_family_transport_frame_absolute_sector_readout_theorem.json"
)


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_artifact(physical_sigma_theorem: dict, sigma_target: dict, absolute_collapse: dict) -> dict:
    target = dict(sigma_target["unique_exact_sigma_target"])
    forced = dict(absolute_collapse["exact_current_family_sigma_specialization"])
    return {
        "artifact": "oph_quark_current_family_transport_frame_absolute_sector_readout_theorem",
        "generated_utc": _timestamp(),
        "proof_status": "closed_current_family_transport_frame_absolute_sector_readout_theorem",
        "theorem_scope": physical_sigma_theorem["theorem_scope"],
        "public_promotion_allowed": False,
        "corresponds_to_global_contract": {
            "id": "quark_absolute_sector_readout_theorem",
            "mathematical_name": "Theta_ud^abs",
            "carrier_restriction": physical_sigma_theorem["theorem_scope"],
        },
        "supporting_artifacts": {
            "restricted_physical_sigma_lift_theorem": physical_sigma_theorem["artifact"],
            "exact_sigma_target": sigma_target["artifact"],
            "absolute_readout_algebraic_collapse": absolute_collapse["artifact"],
        },
        "theorem_statement": (
            "On the explicit current-family common-refinement transport-frame carrier, once the restricted physical "
            "sigma lift provides the Sigma_ud^phys datum and the attached exact sigma target is fixed, the affine mean "
            "law emits the absolute sector scales (g_u, g_d) algebraically. Equivalently, the restricted-carrier "
            "analogue of Theta_ud^abs is closed on that surface."
        ),
        "restricted_sigma_datum": {
            "sigma_id": physical_sigma_theorem["emitted_sigma_ud_phys_element"]["sigma_id"],
            "canonical_token": physical_sigma_theorem["emitted_sigma_ud_phys_element"]["canonical_token"],
            "sigma_u_target": float(target["sigma_u_target"]),
            "sigma_d_target": float(target["sigma_d_target"]),
            "sigma_seed_ud_target": float(target["sigma_seed_ud_target"]),
            "eta_ud_target": float(target["eta_ud_target"]),
        },
        "affine_mean_law": absolute_collapse["fixed_affine_mean_law"],
        "emitted_absolute_sector_scales": {
            "g_u": float(forced["g_u_forced"]),
            "g_d": float(forced["g_d_forced"]),
        },
        "notes": [
            "This theorem is the restricted-carrier analogue of the public contract object quark_absolute_sector_readout_theorem.",
            "It uses the attached exact sigma target on the declared current-family/common-refinement transport-frame surface and does not claim target-free public promotion.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the restricted-carrier quark absolute sector-readout theorem artifact.")
    parser.add_argument("--physical-sigma-theorem", default=str(PHYSICAL_SIGMA_THEOREM_JSON))
    parser.add_argument("--sigma-target", default=str(SIGMA_TARGET_JSON))
    parser.add_argument("--absolute-collapse", default=str(ABSOLUTE_COLLAPSE_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    payload = build_artifact(
        _load_json(Path(args.physical_sigma_theorem)),
        _load_json(Path(args.sigma_target)),
        _load_json(Path(args.absolute_collapse)),
    )
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
