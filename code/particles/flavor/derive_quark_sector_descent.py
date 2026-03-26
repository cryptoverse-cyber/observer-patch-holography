#!/usr/bin/env python3
"""Derive a candidate odd quark-sector splitter from the full flavor observable."""

from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import sys
from datetime import datetime, timezone
from typing import Any

import numpy as np


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_OBSERVABLE = ROOT /  "runs" / "flavor" / "flavor_observable_artifact.json"
DEFAULT_CHARGED_BUDGET = ROOT /  "runs" / "flavor" / "charged_budget_transport.json"
DEFAULT_TENSORS = ROOT /  "runs" / "flavor" / "suppression_phase_tensors.json"
DEFAULT_RESPONSE_LAW = ROOT /  "runs" / "flavor" / "quark_odd_response_law.json"
DEFAULT_OUT = ROOT /  "runs" / "flavor" / "quark_sector_descent.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _as_diag(values: np.ndarray) -> list[float]:
    return [float(x) for x in values.tolist()]


def _yukawa_from_factorized(
    g_scalar: float,
    diag_left: np.ndarray,
    suppression: np.ndarray,
    phase: np.ndarray,
    diag_right: np.ndarray,
) -> np.ndarray:
    return (
        float(g_scalar)
        * np.diag(np.exp(diag_left))
        @ (np.exp(-suppression) * np.exp(1j * phase))
        @ np.diag(np.exp(diag_right))
    )


def build_artifact(response_law: dict[str, Any]) -> dict[str, Any]:
    odd_splitter = np.asarray(response_law["Xi_q_real"], dtype=float) + 1j * np.asarray(response_law["Xi_q_imag"], dtype=float)
    seed = dict(response_law.get("shared_charged_response_seed", {}))
    s_ch = np.asarray(seed["S_ch"], dtype=float)
    phi_ch = np.asarray(seed["Phi_ch"], dtype=float)
    delta_s = np.asarray(response_law["Delta_S_q"], dtype=float)
    delta_phi = np.asarray(response_law["Delta_Phi_q"], dtype=float)
    delta_logd_left = np.asarray(response_law["Delta_logD_left_q"], dtype=float)
    delta_logd_right = np.asarray(response_law["Delta_logD_right_q"], dtype=float)
    delta_logg_q = float(response_law["delta_logg_q"])

    s_u = s_ch + delta_s
    s_d = s_ch - delta_s
    phi_u = phi_ch + delta_phi
    phi_d = phi_ch - delta_phi
    logd_ch_left = np.asarray(seed.get("logD_ch_left", [0.0, 0.0, 0.0]), dtype=float)
    logd_ch_right = np.asarray(seed.get("logD_ch_right", [0.0, 0.0, 0.0]), dtype=float)
    logd_u_left = logd_ch_left + delta_logd_left
    logd_d_left = logd_ch_left - delta_logd_left
    logd_u_right = logd_ch_right + delta_logd_right
    logd_d_right = logd_ch_right - delta_logd_right

    g_ch = float(seed.get("g_ch_candidate", 1.0))
    g_u = g_ch * float(np.exp(delta_logg_q))
    g_d = g_ch * float(np.exp(-delta_logg_q))

    y_u = _yukawa_from_factorized(g_u, logd_u_left, s_u, phi_u, logd_u_right)
    y_d = _yukawa_from_factorized(g_d, logd_d_left, s_d, phi_d, logd_d_right)
    h_u = y_u @ y_u.conj().T
    h_d = y_d @ y_d.conj().T
    commutator = h_u @ h_d - h_d @ h_u
    noncentrality = float(np.linalg.norm(commutator, ord="fro"))

    sector_distinctness = float(
        max(
            np.max(np.abs(s_u - s_d)),
            np.max(np.abs(phi_u - phi_d)),
            np.max(np.abs(logd_u_left - logd_d_left)),
        )
    )
    local_shape_closed = (
        bool(response_law.get("coefficient_free", False))
        and response_law.get("lift_constants") in (None, {})
        and str(response_law.get("delta_logg_q_status", "")) == "closed_zero_corollary"
        and str(response_law.get("lift_parameterization_kind", "")) == "single_kappa_signed_projector_ray"
    )

    return {
        "artifact": "oph_quark_sector_descent",
        "generated_utc": _timestamp(),
        "channel_splitter_kind": "odd_projector_resolved_splitter",
        "proof_status": "odd_splitter_candidate",
        "uses_full_projector_algebra": True,
        "quark_descent_proof_status": (
            "closed"
            if local_shape_closed and not bool(response_law.get("degenerate_placeholder_fallback_used", False))
            else "open"
        ),
        "response_map_id": response_law.get("response_map_id"),
        "coefficient_free": bool(response_law.get("coefficient_free", False)),
        "orientation_fixed": bool(response_law.get("orientation_fixed", False)),
        "delta_logg_q_status": response_law.get("delta_logg_q_status"),
        "shared_scalarization_law_status": response_law.get("shared_scalarization_law_status"),
        "degenerate_placeholder_fallback_used": bool(response_law.get("degenerate_placeholder_fallback_used", False)),
        "projector_split_coefficients": list(response_law.get("projector_split_coefficients", [])),
        "Xi_q_real": np.real(odd_splitter).tolist(),
        "Xi_q_imag": np.imag(odd_splitter).tolist(),
        "Delta_S_q": delta_s.tolist(),
        "Delta_Phi_q": delta_phi.tolist(),
        "Delta_logD_left_q": _as_diag(delta_logd_left),
        "Delta_logD_right_q": _as_diag(delta_logd_right),
        "delta_logg_q": float(delta_logg_q),
        "S_u": s_u.tolist(),
        "S_d": s_d.tolist(),
        "Phi_u": phi_u.tolist(),
        "Phi_d": phi_d.tolist(),
        "D_u_left_log": _as_diag(logd_u_left),
        "D_u_right_log": _as_diag(logd_u_right),
        "D_d_left_log": _as_diag(logd_d_left),
        "D_d_right_log": _as_diag(logd_d_right),
        "g_ch": g_ch,
        "g_u": g_u,
        "g_d": g_d,
        "u_raw_channel_norm_candidate": g_u,
        "d_raw_channel_norm_candidate": g_d,
        "shared_norm_origin": "charged_dirac_scalarization_restriction",
        "shared_norm_status": "numerically_pinned_candidate",
        "even_excitation_theorem_candidate": "oph_family_excitation_evaluator",
        "even_excitation_input_kind": "ordered_branch_generator_spectral_package",
        "even_evaluator_family": "trace_zero_quadratic_on_ordered_branch_generator",
        "ordered_branch_coordinate_formula": "x_a = 2*(lambda_a-lambda_1)/(lambda_3-lambda_1) - 1",
        "even_evaluator_centering_mode": "trace_zero",
        "exact_missing_object": "oph_family_excitation_evaluator",
        "hierarchy_driver_status": "missing_even_excitation_evaluator",
        "E_u_log": None,
        "E_d_log": None,
        "budget_neutrality_certificate": {
            "status": "closed",
            "delta_logg_q": float(delta_logg_q),
            "u_plus_d_odd_part_sum": 0.0,
        },
        "sector_distinctness_witness": {
            "status": "closed" if sector_distinctness > 1.0e-12 else "failed",
            "value": sector_distinctness,
        },
        "noncentrality_witness": {
            "status": "closed" if noncentrality > 1.0e-18 else "failed",
            "fro_norm": noncentrality,
        },
        "dense_entrywise_amplitude_used": False,
        "metadata": {
            "shared_charged_seed_kind": seed.get("seed_kind"),
            "note": "Candidate odd quark-sector descent built from an explicit shared charged response seed plus the separate odd-response-law artifact. The local shape map is explicit and coefficient-free on the current single-kappa ray, and the absolute quark norm is already numerically pinned by the shared charged scalarization candidate. The first mass-moving missing object is now the sector-even family excitation evaluator E_q on the ordered branch-generator spectral package; the best reduced live family is a trace-zero quadratic on the ordered branch coordinate, and further commutator-only polishing is provenance work, not the main hierarchy generator.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Derive a candidate odd quark-sector splitter.")
    parser.add_argument("--observable", default=str(DEFAULT_OBSERVABLE), help="Input flavor observable JSON path.")
    parser.add_argument("--charged-budget", default=str(DEFAULT_CHARGED_BUDGET), help="Input charged-budget JSON path.")
    parser.add_argument("--tensors", default=str(DEFAULT_TENSORS), help="Input suppression/phase tensors JSON path.")
    parser.add_argument("--response-law", default=str(DEFAULT_RESPONSE_LAW), help="Input quark odd-response-law JSON path.")
    parser.add_argument("--output", default=str(DEFAULT_OUT), help="Output quark-sector-descent JSON path.")
    args = parser.parse_args()

    response_path = pathlib.Path(args.response_law)
    if response_path.exists():
        response_law = json.loads(response_path.read_text(encoding="utf-8"))
    else:
        module_path = ROOT /  "flavor" / "derive_quark_odd_response_law.py"
        spec = importlib.util.spec_from_file_location("derive_quark_odd_response_law", module_path)
        if spec is None or spec.loader is None:
            raise SystemExit(f"unable to load {module_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules.setdefault("derive_quark_odd_response_law", module)
        spec.loader.exec_module(module)
        build_response_law = module.build_artifact

        observable = json.loads(pathlib.Path(args.observable).read_text(encoding="utf-8"))
        charged_budget = json.loads(pathlib.Path(args.charged_budget).read_text(encoding="utf-8"))
        tensors = json.loads(pathlib.Path(args.tensors).read_text(encoding="utf-8"))
        response_law = build_response_law(observable, charged_budget, tensors)
    artifact = build_artifact(response_law)

    out_path = pathlib.Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
