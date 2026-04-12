#!/usr/bin/env python3
"""Build a continuation-only Yukawa dictionary sidecar from edge statistics and D12 backread.

Chain role: expose the strongest constructive quark dictionary currently
available when the public theorem lane is still open.

Mathematics: use the direct edge-statistics spread bridge for the even ordered
family and the D12 internal-backread selector value for the odd pure-B payload
and transport lift.

OPH-derived inputs: the explicit edge-statistics spread candidate, the emitted
D12 internal-backread source payload, the current quark descent shape data, and
the D12 overlap transport law.

Output: one continuation-only quark dictionary sidecar carrying explicit
`E_u_log`, `E_d_log`, source payloads, weighted `tau` values, and the induced
forward Yukawa matrices.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EDGE = ROOT / "particles" / "runs" / "flavor" / "quark_edge_statistics_spread_candidate.json"
DEFAULT_SOURCE = ROOT / "particles" / "runs" / "flavor" / "quark_d12_internal_backread_source_payload.json"
DEFAULT_DESCENT = ROOT / "particles" / "runs" / "flavor" / "quark_sector_descent.json"
DEFAULT_OVERLAP = ROOT / "particles" / "runs" / "flavor" / "quark_d12_overlap_transport_law.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "flavor" / "quark_d12_internal_backread_yukawa_dictionary.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _encode_complex_matrix(matrix: np.ndarray) -> dict[str, Any]:
    return {
        "real": np.real(matrix).tolist(),
        "imag": np.imag(matrix).tolist(),
    }


def _sorted_left_diagonalizer(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    hermitian = matrix @ matrix.conj().T
    evals, evecs = np.linalg.eigh(hermitian)
    order = np.argsort(evals)
    evals = np.real_if_close(evals[order])
    evecs = evecs[:, order]
    singular_values = np.sqrt(np.clip(evals, 0.0, None))
    return singular_values, evecs


def _jarlskog(ckm: np.ndarray) -> float:
    return float(np.imag(ckm[0, 0] * ckm[1, 1] * np.conj(ckm[0, 1]) * np.conj(ckm[1, 0])))


def _commutator_invariant(y_u: np.ndarray, y_d: np.ndarray) -> dict[str, float]:
    h_u = y_u @ y_u.conj().T
    h_d = y_d @ y_d.conj().T
    commutator = h_u @ h_d - h_d @ h_u
    det_value = np.linalg.det(commutator)
    return {
        "fro_norm": float(np.linalg.norm(commutator, ord="fro")),
        "det_abs": float(abs(det_value)),
        "det_imag": float(np.imag(det_value)),
    }


def _build_factorized_matrix(payload: dict[str, Any], prefix: str, even_log: list[float]) -> np.ndarray:
    suppression = np.asarray(payload[f"S_{prefix}"], dtype=float)
    phase = np.asarray(payload[f"Phi_{prefix}"], dtype=float)
    log_left = np.asarray(payload[f"D_{prefix}_left_log"], dtype=float)
    log_right = np.asarray(payload[f"D_{prefix}_right_log"], dtype=float)
    g_scalar = float(payload[f"g_{prefix}"])
    even = np.asarray(even_log, dtype=float)
    return (
        g_scalar
        * np.diag(np.exp(log_left + even))
        @ (np.exp(-suppression) * np.exp(1j * phase))
        @ np.diag(np.exp(log_right + even))
    )


def build_artifact(
    edge_candidate: dict[str, Any],
    source_payload: dict[str, Any],
    descent: dict[str, Any],
    overlap_law: dict[str, Any] | None = None,
) -> dict[str, Any]:
    overlap_law = overlap_law or {}

    sigma_u = float(edge_candidate["candidate_sigmas"]["sigma_u_total_log_per_side"])
    sigma_d = float(edge_candidate["candidate_sigmas"]["sigma_d_total_log_per_side"])
    delta = float(source_payload["Delta_ud_overlap"])
    beta_u = float(source_payload["beta_u_diag_B_source"])
    beta_d = float(source_payload["beta_d_diag_B_source"])
    b_ord = [float(value) for value in source_payload["B_ord"]]
    v_u = [float(value) for value in edge_candidate["profile_rays"]["v_u"]]
    v_d = [float(value) for value in edge_candidate["profile_rays"]["v_d"]]

    e_u_base = [sigma_u * value for value in v_u]
    e_d_base = [sigma_d * value for value in v_d]

    edge_branch = (
        dict((overlap_law.get("sigma_branch_contracts") or {}).get("edge_statistics_bridge_sigma_pair") or {})
        if overlap_law
        else {}
    )
    internal_transport = dict(edge_branch.get("internal_backread_realization") or {})
    if internal_transport:
        tau_u = float(internal_transport["tau_u_log_per_side"])
        tau_d = float(internal_transport["tau_d_log_per_side"])
        lambda_b = float(internal_transport["Lambda_ud_B_transport"])
        tau_formula_kind = "explicit_edge_branch_overlap_law_internal_backread_realization"
    else:
        denom = 2.0 * (sigma_u + sigma_d)
        tau_u = sigma_d * delta / denom
        tau_d = sigma_u * delta / denom
        lambda_b = sigma_u * sigma_d * delta / denom
        tau_formula_kind = "D12_weighted_overlap_transport_from_edge_bridge_sigmas"

    e_u_lifted = [base + (tau_u * b) for base, b in zip(e_u_base, b_ord, strict=True)]
    e_d_lifted = [base + (tau_d * b) for base, b in zip(e_d_base, b_ord, strict=True)]

    y_u = _build_factorized_matrix(descent, "u", e_u_lifted)
    y_d = _build_factorized_matrix(descent, "d", e_d_lifted)
    masses_u, u_left = _sorted_left_diagonalizer(y_u)
    masses_d, d_left = _sorted_left_diagonalizer(y_d)
    ckm = u_left.conj().T @ d_left

    theorem_overlap = dict(overlap_law.get("sample_same_family_point", {}))
    theorem_tau_u = theorem_overlap.get("tau_u_log_per_side")
    theorem_tau_d = theorem_overlap.get("tau_d_log_per_side")

    return {
        "artifact": "oph_quark_d12_internal_backread_yukawa_dictionary",
        "generated_utc": _timestamp(),
        "scope": "D12_continuation_internal_backread_only",
        "proof_status": "internal_backread_edge_bridge_dictionary_emitted",
        "public_promotion_allowed": False,
        "changes_public_theorem_frontier": False,
        "source_artifacts": {
            "edge_statistics_spread_candidate": edge_candidate.get("artifact"),
            "internal_backread_source_payload": source_payload.get("artifact"),
            "quark_sector_descent_shape_data": descent.get("artifact"),
            "d12_overlap_transport_law": overlap_law.get("artifact"),
        },
        "even_dictionary": {
            "sigma_source_kind": "edge_statistics_bridge_candidate",
            "sigma_u_total_log_per_side": sigma_u,
            "sigma_d_total_log_per_side": sigma_d,
            "profile_rays": {
                "v_u": v_u,
                "v_d": v_d,
            },
            "E_u_log_base": e_u_base,
            "E_d_log_base": e_d_base,
        },
        "odd_source_payload": {
            "Delta_ud_overlap": delta,
            "beta_u_diag_B_source": beta_u,
            "beta_d_diag_B_source": beta_d,
            "source_readback_u_log_per_side": source_payload["source_readback_u_log_per_side"],
            "source_readback_d_log_per_side": source_payload["source_readback_d_log_per_side"],
            "J_B_source_u": source_payload["J_B_source_u"],
            "J_B_source_d": source_payload["J_B_source_d"],
            "B_ord": b_ord,
        },
        "odd_transport_lift": {
            "tau_formula_kind": tau_formula_kind,
            "tau_u_log_per_side": float(tau_u),
            "tau_d_log_per_side": float(tau_d),
            "Lambda_ud_B_transport": float(lambda_b),
            "tau_u_formula": "sigma_d_total_log_per_side * Delta_ud_overlap / (2 * (sigma_u_total_log_per_side + sigma_d_total_log_per_side))",
            "tau_d_formula": "sigma_u_total_log_per_side * Delta_ud_overlap / (2 * (sigma_u_total_log_per_side + sigma_d_total_log_per_side))",
            "Lambda_ud_B_transport_formula": "sigma_u_total_log_per_side * sigma_d_total_log_per_side * Delta_ud_overlap / (2 * (sigma_u_total_log_per_side + sigma_d_total_log_per_side))",
            "tau_sum_half_delta_identity": float((tau_u + tau_d) - (0.5 * delta)),
            "tau_ratio_minus_sigma_ratio": float((tau_d / tau_u) - (sigma_u / sigma_d)),
            "comparison_to_theorem_mean_surface_sample": {
                "sample_exists": theorem_tau_u is not None and theorem_tau_d is not None,
                "tau_u_residual_vs_sample": None if theorem_tau_u is None else float(tau_u - float(theorem_tau_u)),
                "tau_d_residual_vs_sample": None if theorem_tau_d is None else float(tau_d - float(theorem_tau_d)),
                "reason": "The live D12 overlap law still uses the theorem-mean-surface sigma pair, while this sidecar intentionally uses the direct edge-statistics sigma pair.",
            },
            "consumed_overlap_law_artifact": overlap_law.get("artifact"),
        },
        "lifted_even_logs": {
            "E_u_log": e_u_lifted,
            "E_d_log": e_d_lifted,
            "lift_formula_u": "E_u_log_base + tau_u_log_per_side * B_ord",
            "lift_formula_d": "E_d_log_base + tau_d_log_per_side * B_ord",
        },
        "sector_means": {
            "g_u": float(descent["g_u"]),
            "g_d": float(descent["g_d"]),
            "shared_norm_origin": descent.get("shared_norm_origin"),
        },
        "forward_surface": {
            "Y_u": _encode_complex_matrix(y_u),
            "Y_d": _encode_complex_matrix(y_d),
            "singular_values_u": [float(value) for value in masses_u.tolist()],
            "singular_values_d": [float(value) for value in masses_d.tolist()],
            "U_u_left": _encode_complex_matrix(u_left),
            "U_d_left": _encode_complex_matrix(d_left),
            "V_CKM": _encode_complex_matrix(ckm),
            "jarlskog": _jarlskog(ckm),
            "commutator_invariant": _commutator_invariant(y_u, y_d),
        },
        "notes": [
            "This is the first explicit quark Yukawa-dictionary sidecar in the repo that combines the direct edge-statistics spread bridge with an emitted pure-B source payload object.",
            "The sidecar is intentionally continuation-only and internal-backread-only. It records a constructive dictionary surface without claiming that the public theorem-grade quark lane has closed.",
            "Its odd transport lift uses the weighted D12 overlap law tau_q = sigma_{other} * Delta_ud_overlap / (2 * (sigma_u + sigma_d)), not the raw source-side beta pair.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the D12 internal-backread quark Yukawa dictionary sidecar.")
    parser.add_argument("--edge-candidate", default=str(DEFAULT_EDGE))
    parser.add_argument("--source-payload", default=str(DEFAULT_SOURCE))
    parser.add_argument("--descent", default=str(DEFAULT_DESCENT))
    parser.add_argument("--overlap-law", default=str(DEFAULT_OVERLAP))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    edge_candidate = json.loads(Path(args.edge_candidate).read_text(encoding="utf-8"))
    source_payload = json.loads(Path(args.source_payload).read_text(encoding="utf-8"))
    descent = json.loads(Path(args.descent).read_text(encoding="utf-8"))
    overlap_path = Path(args.overlap_law)
    overlap_law = json.loads(overlap_path.read_text(encoding="utf-8")) if overlap_path.exists() else None
    artifact = build_artifact(edge_candidate, source_payload, descent, overlap_law=overlap_law)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
