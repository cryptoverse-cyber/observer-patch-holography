#!/usr/bin/env python3
"""Emit the restricted-carrier physical sigma-lift theorem for the quark lane."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LIFT_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_transport_frame_sector_attached_lift.json"
DEFAULT_OUT = (
    ROOT / "particles" / "runs" / "flavor" / "quark_current_family_transport_frame_physical_sigma_lift_theorem.json"
)


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_artifact(lift: dict) -> dict:
    emitted = dict(lift["emitted_sigma_ud_phys_element"])
    return {
        "artifact": "oph_quark_current_family_transport_frame_physical_sigma_lift_theorem",
        "generated_utc": _timestamp(),
        "proof_status": "closed_current_family_transport_frame_physical_sigma_lift_theorem",
        "theorem_scope": lift["theorem_scope"],
        "public_promotion_allowed": False,
        "corresponds_to_global_contract": {
            "id": "quark_physical_sigma_ud_lift",
            "mathematical_name": "Theta_ud^phys",
            "carrier_restriction": lift["theorem_scope"],
        },
        "supporting_sector_attachment_artifact": lift["artifact"],
        "theorem_statement": (
            "On the explicit current-family common-refinement transport-frame carrier, the same-label line-lift "
            "transport data determine a sector-attached element of Sigma_ud^phys over the frame class [F0^dagger F1]. "
            "Equivalently, the restricted-carrier analogue of Theta_ud^phys is closed on that declared surface."
        ),
        "physical_carrier": lift["physical_carrier"],
        "restricted_section_theorem": {
            "domain": lift["section_property"]["section_domain"],
            "projection": lift["section_property"]["projection"],
            "pi_of_emitted_element_equals_frame_class": lift["section_property"]["pi_of_emitted_element_equals_frame_class"],
        },
        "emitted_sigma_ud_phys_element": emitted,
        "common_refinement_frame_class": lift["common_refinement_frame_class"],
        "quotient_well_definedness": lift["quotient_well_definedness"],
        "attached_exact_sigma_target": lift["strengthened_sigma_data"],
        "notes": [
            "This theorem is the restricted-carrier analogue of the public contract object quark_physical_sigma_ud_lift.",
            "It does not claim target-free public promotion beyond the declared current-family/common-refinement transport-frame surface.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the restricted-carrier quark physical sigma-lift theorem artifact.")
    parser.add_argument("--lift", default=str(LIFT_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    payload = build_artifact(_load_json(Path(args.lift)))
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
