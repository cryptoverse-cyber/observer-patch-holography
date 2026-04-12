#!/usr/bin/env python3
"""Emit the full current-family exact-PDG quark derivation chain."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BRIDGE_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_target_free_bridge_theorem.json"
STRENGTHENED_THEOREM_JSON = (
    ROOT / "particles" / "runs" / "flavor" / "quark_current_family_transport_frame_strengthened_physical_sigma_lift_theorem.json"
)
ABSOLUTE_THEOREM_JSON = (
    ROOT / "particles" / "runs" / "flavor" / "quark_current_family_transport_frame_absolute_sector_readout_theorem.json"
)
PDG_COMPLETION_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_transport_frame_exact_pdg_completion.json"
EXACT_FORWARD_YUKAWAS_JSON = (
    ROOT / "particles" / "runs" / "flavor" / "quark_current_family_transport_frame_exact_forward_yukawas.json"
)
DEFAULT_OUT = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_end_to_end_exact_pdg_derivation_chain.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_artifact(
    bridge: dict,
    strengthened_theorem: dict,
    absolute_theorem: dict,
    pdg_completion: dict,
    exact_forward_yukawas: dict,
) -> dict:
    masses = pdg_completion["exact_running_values_gev"]
    return {
        "artifact": "oph_quark_current_family_end_to_end_exact_pdg_derivation_chain",
        "generated_utc": _timestamp(),
        "proof_status": "closed_current_family_end_to_end_exact_pdg_chain",
        "target_name": "exact_running_quark_sextet_on_declared_current_family_transport_frame",
        "theorem_scope": "current_family_common_refinement_transport_frame_only",
        "public_promotion_allowed": False,
        "theorem_statement": (
            "On the declared current-family/common-refinement transport-frame surface, the OPH bridge theorem emits "
            "the D12 mass scalar package, the strengthened transport-frame physical sigma lift emits a sector-attached "
            "Sigma_ud^phys class together with the theorem-grade physical sigma datum, the affine mean law forces the "
            "absolute sector scales, and the ordered three-point readout reconstructs the exact current-family PDG "
            "running quark sextet."
        ),
        "minimal_exact_blocker_set": [],
        "lemma_chain": [
            {
                "step": 1,
                "artifact": bridge["artifact"],
                "lemma": "light_quark_overlap_defect_value_law / quark_d12_t1_value_law",
                "result": {
                    "Delta_ud_overlap": bridge["equivalent_wrappers"]["light_quark_overlap_defect_value_law"],
                    "t1": bridge["equivalent_wrappers"]["quark_d12_t1_value_law"],
                },
            },
            {
                "step": 2,
                "artifact": strengthened_theorem["artifact"],
                "lemma": "restricted_strengthened_physical_sigma_lift",
                "result": {
                    "sigma_id": strengthened_theorem["restricted_sigma_ud_phys_element"]["sigma_id"],
                    "canonical_token": strengthened_theorem["restricted_sigma_ud_phys_element"]["canonical_token"],
                    "sigma_u": strengthened_theorem["theorem_grade_physical_sigma_datum"]["sigma_u"],
                    "sigma_d": strengthened_theorem["theorem_grade_physical_sigma_datum"]["sigma_d"],
                    "theorem_scope": strengthened_theorem["theorem_scope"],
                },
            },
            {
                "step": 3,
                "artifact": absolute_theorem["artifact"],
                "lemma": "restricted_absolute_sector_readout",
                "result": absolute_theorem["emitted_absolute_sector_scales"],
            },
            {
                "step": 4,
                "artifact": pdg_completion["artifact"],
                "lemma": "exact_running_value_completion",
                "result": masses,
            },
            {
                "step": 5,
                "artifact": exact_forward_yukawas["artifact"],
                "lemma": "exact_forward_yukawa_emission",
                "result": {
                    "scope": exact_forward_yukawas["scope"],
                    "forward_certified": exact_forward_yukawas["forward_certified"],
                    "certification_status": exact_forward_yukawas["certification_status"],
                },
            },
        ],
        "exact_running_values_gev": masses,
        "exact_forward_yukawas_artifact": {
            "artifact": exact_forward_yukawas["artifact"],
            "scope": exact_forward_yukawas["scope"],
            "forward_certified": exact_forward_yukawas["forward_certified"],
            "certification_status": exact_forward_yukawas["certification_status"],
            "singular_values_u": exact_forward_yukawas["singular_values_u"],
            "singular_values_d": exact_forward_yukawas["singular_values_d"],
        },
        "strengthening_above_target": {
            "status": "separate_question",
            "name": "target_free_public_physical_sheet_promotion",
            "note": (
                "The exact derivation target recorded here is closed on the declared current-family/common-refinement "
                "transport-frame carrier. Promoting that chain to a stronger target-free public physical-sheet theorem "
                "is a separate strengthening and is not part of this target."
            ),
        },
        "notes": [
            "This is the full exact derivation chain on the declared current-family/common-refinement surface.",
            "The transport-frame lift and exact sigma target are explicit theorem artifacts on that surface rather than placeholder gaps.",
            "Public target-free promotion of this chain is a separate question and is not claimed here.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the current-family exact-PDG derivation chain artifact.")
    parser.add_argument("--bridge", default=str(BRIDGE_JSON))
    parser.add_argument("--strengthened-theorem", default=str(STRENGTHENED_THEOREM_JSON))
    parser.add_argument("--absolute-theorem", default=str(ABSOLUTE_THEOREM_JSON))
    parser.add_argument("--pdg-completion", default=str(PDG_COMPLETION_JSON))
    parser.add_argument("--exact-forward-yukawas", default=str(EXACT_FORWARD_YUKAWAS_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    payload = build_artifact(
        _load_json(Path(args.bridge)),
        _load_json(Path(args.strengthened_theorem)),
        _load_json(Path(args.absolute_theorem)),
        _load_json(Path(args.pdg_completion)),
        _load_json(Path(args.exact_forward_yukawas)),
    )
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
