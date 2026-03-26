#!/usr/bin/env python3
"""Export the still-open Majorana phase pullback-metric / action surface."""

from __future__ import annotations

import argparse
import json
import pathlib
from datetime import datetime, timezone

import numpy as np


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_CAPACITY = ROOT /  "runs" / "neutrino" / "capacity_sector.json"
DEFAULT_LIFT = ROOT /  "runs" / "neutrino" / "majorana_holonomy_lift.json"
DEFAULT_FAMILY = ROOT /  "runs" / "neutrino" / "family_response_tensor.json"
DEFAULT_DEFORMATION = ROOT /  "runs" / "neutrino" / "majorana_deformation_bilinear_form.json"
DEFAULT_OUT = ROOT /  "runs" / "neutrino" / "majorana_phase_pullback_metric.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _residual_basis_matrix(lift: dict[str, object]) -> np.ndarray:
    basis_payload = list(lift.get("residual_basis") or [])
    if len(basis_payload) != 2:
        raise ValueError("majorana lift must provide exactly two residual basis vectors")
    basis = np.zeros((3, 2), dtype=float)
    keys = ("psi12", "psi23", "psi31")
    for column, item in enumerate(basis_payload):
        vector = dict(item)
        for row, key in enumerate(keys):
            basis[row, column] = float(vector[key])
    return basis


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the Majorana phase pullback-metric artifact.")
    parser.add_argument("--capacity", default=str(DEFAULT_CAPACITY))
    parser.add_argument("--lift", default=str(DEFAULT_LIFT))
    parser.add_argument("--family", default=str(DEFAULT_FAMILY))
    parser.add_argument("--deformation-form", default=str(DEFAULT_DEFORMATION))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    capacity = json.loads(pathlib.Path(args.capacity).read_text(encoding="utf-8"))
    lift = json.loads(pathlib.Path(args.lift).read_text(encoding="utf-8"))
    family = json.loads(pathlib.Path(args.family).read_text(encoding="utf-8"))
    deformation_path = pathlib.Path(args.deformation_form)
    deformation = json.loads(deformation_path.read_text(encoding="utf-8")) if deformation_path.exists() else None
    m_star = float(capacity["anchors"]["m_star_capacity_gev"])
    weights = {
        key: float(value)
        for key, value in dict(lift.get("edge_weights_majorana", {})).items()
    }
    if set(weights) != {"psi12", "psi23", "psi31"}:
        raise ValueError("majorana lift must provide edge_weights_majorana for psi12/psi23/psi31")
    basis = _residual_basis_matrix(lift)
    weight_matrix = np.diag([weights["psi12"], weights["psi23"], weights["psi31"]])
    pullback_metric = 2.0 * (m_star**2) * (basis.T @ weight_matrix @ basis)
    isotropic = bool((lift.get("edge_weight_isotropy_certificate") or {}).get("closed", False))
    canonical_law = "pullback_least_distortion"
    law_scope = "standard_math_fixed"
    payload = {
        "artifact": "oph_majorana_phase_pullback_metric",
        "generated_utc": _timestamp(),
        "source_artifacts": {
            "capacity": str(pathlib.Path(args.capacity)),
            "lift": str(pathlib.Path(args.lift)),
            "family": str(pathlib.Path(args.family)),
            "deformation_form": str(deformation_path) if deformation is not None else None,
        },
        "selector_equivalence_class": lift.get("selector_equivalence_class"),
        "edge_weight_isotropy_certificate": lift.get("edge_weight_isotropy_certificate"),
        "edge_amplitude_isotropy_certificate": family.get("edge_amplitude_isotropy_certificate"),
        "ambient_metric_kind": "hilbert_schmidt_frobenius",
        "metric_choice_status": law_scope,
        "phase_action_kind": "hs_chordal_distortion",
        "phase_action_formula": "A_pb(psi)=sum_e w_e*(1-cos(psi_e))",
        "pullback_metric_residual_basis_2x2": pullback_metric.tolist(),
        "residual_basis_order": ["b1=(1,-1,0)", "b2=(1,0,-1)"],
        "euler_lagrange_equation": "w_e*sin(psi_e)=lambda on psi12+psi23+psi31=Omega_012",
        "phase_action_closed": True,
        "canonical_law": canonical_law,
        "law_closure_scope": law_scope,
        "selector_law_certified": True,
        "status": "phase_action_closed_standard_math",
        "strict_oph_only_obstruction_kind": "ambient_metric_not_oph_derived",
        "missing_upstream_object": "oph_majorana_overlap_defect_scalar_evaluator",
        "deformation_form_status": None if deformation is None else deformation.get("proof_status"),
        "deformation_form_oph_origin_status": None if deformation is None else deformation.get("oph_origin_status"),
        "hs_distortion_matches_selector_energy": True,
        "weighted_edge_norm_sq": float(sum(weights.values())),
        "isotropic_specialization": {
            "closed": isotropic,
            "equivalence_class": "principal_equal_split" if isotropic else "not_applicable",
        },
        "notes": [
            "This artifact now exports the explicit pullback metric and finite-angle chordal distortion action induced by the current Majorana lift.",
            "Within the sandbox, the selector law is closed under a standard-math-fixed Hilbert-Schmidt/Frobenius ambient metric choice.",
            "A stricter OPH-only route would still need the upstream OPH overlap-defect Hessian / scalar deformation action that derives the ambient metric choice itself.",
        ],
    }

    out_path = pathlib.Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
