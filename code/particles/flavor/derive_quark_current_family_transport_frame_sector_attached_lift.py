#!/usr/bin/env python3
"""Emit a constructive current-family transport-frame lift into Sigma_ud^phys.

This theorem is deliberately scoped to the explicit current-family/common-
refinement surface. It does not claim target-free public promotion. The point is
to stop treating the common-refinement transport-frame class as purely
diagnostic once the ordered principal frames and the exact current-family sigma
target are both on disk.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from derive_quark_transport_frame_diagnostic_orbit import (
    _align_target_phase,
    _ckm_tuple,
    _decode_complex_matrix,
    _encode_complex_matrix,
    _principal_vector_from_projector,
)


ROOT = Path(__file__).resolve().parents[2]
LINE_LIFT_JSON = ROOT / "particles" / "runs" / "flavor" / "overlap_edge_line_lift.json"
TRANSPORT_FRAME_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_transport_frame_diagnostic_orbit.json"
SIGMA_TARGET_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_exact_sigma_target.json"
DEFAULT_OUT = (
    ROOT / "particles" / "runs" / "flavor" / "quark_current_family_transport_frame_sector_attached_lift.json"
)


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _reconstruct_frames(line_lift: dict) -> tuple[np.ndarray, np.ndarray]:
    items = list(line_lift["transport_partial_isometry_by_label_and_refinement_pair"])
    source_frame = []
    target_frame = []
    for item in items:
        source_projector = _decode_complex_matrix(item["source_projector"])
        target_projector = _decode_complex_matrix(item["target_projector"])
        transport_map = _decode_complex_matrix(item["transport_map"])

        source_vector = _principal_vector_from_projector(source_projector)
        target_vector = _principal_vector_from_projector(target_projector)
        target_vector = _align_target_phase(source_vector, target_vector, transport_map)

        source_frame.append(source_vector)
        target_frame.append(target_vector)

    return np.column_stack(source_frame), np.column_stack(target_frame)


def build_artifact(line_lift: dict, transport_frame: dict, sigma_target: dict) -> dict:
    frame_source, frame_target = _reconstruct_frames(line_lift)
    v_ckm = frame_source.conj().T @ frame_target
    stored_v = _decode_complex_matrix(transport_frame["self_overlap"]["matrix"])
    v_residual = float(np.linalg.norm(v_ckm - stored_v, ord="fro"))

    sigma_target_payload = sigma_target["unique_exact_sigma_target"]
    ckm = _ckm_tuple(v_ckm)
    canonical_token = "CR::same_label_left::transport_frame::current_family_exact"
    sigma_id = "sigma_phys_transport_frame_current_family"

    return {
        "artifact": "oph_quark_current_family_transport_frame_sector_attached_lift",
        "generated_utc": _timestamp(),
        "proof_status": "closed_current_family_sector_attached_transport_frame_lift",
        "theorem_scope": "current_family_common_refinement_transport_frame_only",
        "public_promotion_allowed": False,
        "supporting_artifacts": {
            "line_lift": "code/particles/runs/flavor/overlap_edge_line_lift.json",
            "transport_frame_diagnostic_orbit": "code/particles/runs/flavor/quark_transport_frame_diagnostic_orbit.json",
            "exact_sigma_target": "code/particles/runs/flavor/quark_current_family_exact_sigma_target.json",
        },
        "theorem_statement": (
            "On the explicit current-family common-refinement transport-frame surface, the ordered rank-one same-label "
            "projectors determine source and target unitary frames F0,F1 up to independent diagonal phases, and the "
            "same-label transport maps fix a canonical phase-lock per label. Therefore the tuple "
            "[(sigma_id,tau,U_uL,U_dL,V_CKM,I_CKM)] := "
            "[(sigma_phys_transport_frame_current_family, tau_cf, F0, F1, F0^dagger F1, I(F0^dagger F1))] "
            "is a well-defined element of Sigma_ud^phys over the class [F0^dagger F1]."
        ),
        "physical_carrier": {
            "name": "Sigma_ud^phys",
            "definition": "{(sigma_id, tau, U_uL, U_dL, V_CKM, I_CKM) : V_CKM = U_uL^dagger U_dL} / ~",
            "equivalence_relation": "(U_uL, U_dL, V) ~ (U_uL D_u, U_dL D_d, D_u^dagger V D_d) for diagonal D_u, D_d in U(1)^3",
        },
        "common_refinement_frame_class": {
            "symbol": "[F0^dagger F1]",
            "representative": _encode_complex_matrix(v_ckm),
            "representative_abs_matrix": np.abs(v_ckm).tolist(),
            "matches_transport_frame_diagnostic_fro_residual": v_residual,
        },
        "emitted_sigma_ud_phys_element": {
            "sigma_id": sigma_id,
            "tau": canonical_token,
            "canonical_token": canonical_token,
            "U_u_left": _encode_complex_matrix(frame_source),
            "U_d_left": _encode_complex_matrix(frame_target),
            "V_CKM": _encode_complex_matrix(v_ckm),
            "ckm_invariants": ckm,
        },
        "section_property": {
            "projection": "pi[(sigma_id,tau,U_uL,U_dL,V_CKM,I_CKM)] = [V_CKM]",
            "pi_of_emitted_element_equals_frame_class": True,
            "section_domain": "the explicit common-refinement transport-frame class generated by the same-label line lift",
        },
        "quotient_well_definedness": {
            "phase_ambiguity": "Changing the unit eigenvector representatives multiplies F0 and F1 on the right by diagonal phases D_u,D_d.",
            "induced_action": "F0^dagger F1 -> D_u^dagger (F0^dagger F1) D_d",
            "carrier_compatibility": "This is exactly the defining equivalence relation of Sigma_ud^phys.",
            "conclusion": "The emitted class is independent of the representative eigenvector phases.",
        },
        "strengthened_sigma_data": {
            "status": "attached_exact_current_family_sigma_target",
            "sigma_seed_ud_target": float(sigma_target_payload["sigma_seed_ud_target"]),
            "eta_ud_target": float(sigma_target_payload["eta_ud_target"]),
            "sigma_u_target": float(sigma_target_payload["sigma_u_target"]),
            "sigma_d_target": float(sigma_target_payload["sigma_d_target"]),
        },
        "notes": [
            "This closes the sector attachment only on the declared current-family/common-refinement surface.",
            "It does not claim target-free public promotion of Theta_ud^phys from the present public corpus.",
            "The exact sigma pair attached here is the unique current-family target extracted from the fixed affine readout law.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the current-family transport-frame sector-attached lift artifact.")
    parser.add_argument("--line-lift", default=str(LINE_LIFT_JSON))
    parser.add_argument("--transport-frame", default=str(TRANSPORT_FRAME_JSON))
    parser.add_argument("--sigma-target", default=str(SIGMA_TARGET_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    payload = build_artifact(
        _load_json(Path(args.line_lift)),
        _load_json(Path(args.transport_frame)),
        _load_json(Path(args.sigma_target)),
    )
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
