#!/usr/bin/env python3
"""Emit a continuation-only D12 quark mass-side backread closure sidecar.

Chain role: record the strongest internal D12 continuation closure supported by
the supplied backread assumptions without changing the public theorem frontier.

Mathematics: use the emitted reference-free forward light-quark pair together
with the D12 continuation assumptions
`c_u / c_d = y_u / y_d = m_u / m_d` and
`Delta_ud_overlap = (1/6) * log(c_d / c_u)`.

Output: a continuation-only sidecar that fixes the mass-side scalar package
numerically on the internal D12 backread surface while leaving the public
theorem-grade frontier and the wrong-sheet CKM boundary unchanged.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FORWARD_YUKAWAS = ROOT / "particles" / "runs" / "flavor" / "forward_yukawas.json"
MASS_RAY = ROOT / "particles" / "runs" / "flavor" / "quark_d12_mass_ray.json"
SELECTOR_LAW = ROOT / "particles" / "runs" / "flavor" / "light_quark_isospin_overlap_defect_selector_law.json"
SPREAD_MAP = ROOT / "particles" / "runs" / "flavor" / "quark_spread_map.json"
EDGE_BRIDGE = ROOT / "particles" / "runs" / "flavor" / "quark_edge_statistics_spread_candidate.json"
DEFAULT_OUT = (
    ROOT
    / "particles"
    / "runs"
    / "flavor"
    / "quark_d12_internal_backread_continuation_closure.json"
)


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _weighted_transport_branch(delta_value: float, sigma_u: float, sigma_d: float) -> dict[str, float]:
    denom = 2.0 * (sigma_u + sigma_d)
    tau_u = sigma_d * delta_value / denom
    tau_d = sigma_u * delta_value / denom
    lam = sigma_u * sigma_d * delta_value / denom
    return {
        "tau_u_log_per_side": float(tau_u),
        "tau_d_log_per_side": float(tau_d),
        "Lambda_ud_B_transport": float(lam),
        "tau_sum_half_delta_identity": float((tau_u + tau_d) - (0.5 * delta_value)),
        "tau_ratio_minus_sigma_ratio": float((tau_d / tau_u) - (sigma_u / sigma_d)),
    }


def build_payload(
    forward_yukawas: dict[str, Any],
    mass_ray: dict[str, Any],
    selector_law: dict[str, Any],
    spread_map: dict[str, Any] | None = None,
    edge_bridge: dict[str, Any] | None = None,
) -> dict[str, Any]:
    m_u = float(forward_yukawas["singular_values_u"][0])
    m_d = float(forward_yukawas["singular_values_d"][0])
    cu_over_cd = m_u / m_d
    log_cd_over_cu = math.log(m_d / m_u)
    delta_ud_overlap = log_cd_over_cu / 6.0
    beta_u = delta_ud_overlap / 2.0
    beta_d = -beta_u
    t1 = 5.0 * delta_ud_overlap
    x2 = float(mass_ray["same_family_ray"]["ordered_family_coordinate_x2"])
    eta_q_centered = -((1.0 - x2 * x2) / 27.0) * t1
    kappa_q = -t1 / 54.0
    b_ord = [float(value) for value in selector_law.get("B_ord") or (-1.0, 0.0, 1.0)]
    source_u = [beta_u * value for value in b_ord]
    source_d = [beta_d * value for value in b_ord]
    weighted_transport_by_sigma_branch: dict[str, Any] = {}
    if spread_map is not None:
        sigma_u = float(spread_map["sigma_u_total_log_per_side"])
        sigma_d = float(spread_map["sigma_d_total_log_per_side"])
        weighted_transport_by_sigma_branch["main_builder_sigma_pair"] = {
            "provider_artifact": spread_map.get("artifact"),
            "provider_status": spread_map.get("spread_emitter_status"),
            "sigma_source_kind": spread_map.get("sigma_source_kind"),
            "sigma_u_total_log_per_side": sigma_u,
            "sigma_d_total_log_per_side": sigma_d,
            **_weighted_transport_branch(delta_ud_overlap, sigma_u, sigma_d),
        }
    if edge_bridge is not None:
        sigma_u = float(edge_bridge["candidate_sigmas"]["sigma_u_total_log_per_side"])
        sigma_d = float(edge_bridge["candidate_sigmas"]["sigma_d_total_log_per_side"])
        weighted_transport_by_sigma_branch["edge_statistics_bridge_sigma_pair"] = {
            "provider_artifact": edge_bridge.get("artifact"),
            "provider_status": edge_bridge.get("bridge_status"),
            "sigma_source_kind": edge_bridge.get("candidate_kind"),
            "sigma_u_total_log_per_side": sigma_u,
            "sigma_d_total_log_per_side": sigma_d,
            **_weighted_transport_branch(delta_ud_overlap, sigma_u, sigma_d),
        }
    return {
        "artifact": "oph_quark_d12_internal_backread_continuation_closure",
        "generated_utc": _timestamp(),
        "scope": "D12_continuation_internal_backread_only",
        "proof_status": "internal_backread_mass_side_continuation_closed",
        "public_promotion_allowed": False,
        "theorem_grade_promotion_allowed": False,
        "changes_public_theorem_frontier": False,
        "changes_active_builder_artifacts": False,
        "closure_surface": "mass_side_numeric_package_closed_ckm_branch_open",
        "public_theorem_frontier_still": {
            "broader_honest_primitive": "Delta_ud_overlap",
            "emitted_ray_packaging": "quark_d12_t1_value_law",
            "derived_wrapper": "intrinsic_scale_law_D12",
        },
        "broader_physical_residual": "branch_change_to_physical_ckm_shell",
        "active_builder_residual_on_primary_path": "source_readback_u_log_per_side_and_source_readback_d_log_per_side",
        "continuation_assumptions": [
            "minimal_light_branch_equal_exponents: y_u = c_u * epsilon^6 and y_d = c_d * epsilon^6",
            "same_forward_surface_ratio_identification: c_u / c_d = y_u / y_d = m_u / m_d",
            "D12_normalization: Delta_ud_overlap = (1/6) * log(c_d / c_u)",
            "odd_budget_neutrality: beta_u_diag_B_source + beta_d_diag_B_source = 0",
            "pure_B_readback_shape: source_readback_q_log_per_side = beta_q_diag_B_source * B_ord",
        ],
        "supporting_inputs": {
            "forward_yukawas_artifact": forward_yukawas["artifact"],
            "mass_ray_artifact": mass_ray["artifact"],
            "selector_law_artifact": selector_law["artifact"],
        },
        "forward_reference_free_light_pair_gev": {
            "u": m_u,
            "d": m_d,
        },
        "coefficient_ratio": {
            "c_u_over_c_d": cu_over_cd,
            "log_c_d_over_c_u": log_cd_over_cu,
        },
        "closed_mass_side_package": {
            "Delta_ud_overlap": delta_ud_overlap,
            "t1": t1,
            "eta_Q_centered": eta_q_centered,
            "kappa_Q": kappa_q,
        },
        "closed_source_side_package": {
            "B_ord": b_ord,
            "beta_u_diag_B_source": beta_u,
            "beta_d_diag_B_source": beta_d,
            "source_readback_u_log_per_side": source_u,
            "source_readback_d_log_per_side": source_d,
            "J_B_source_u": beta_u,
            "J_B_source_d": beta_d,
            "tau_u_log_per_side_note": "weighted transport tau_u depends on the chosen sigma branch and is recorded separately",
            "tau_d_log_per_side_note": "weighted transport tau_d depends on the chosen sigma branch and is recorded separately",
        },
        "closed_weighted_transport_by_sigma_branch": weighted_transport_by_sigma_branch,
        "consistency_checks": {
            "delta_minus_t1_over_5": delta_ud_overlap - (t1 / 5.0),
            "eta_minus_formula": eta_q_centered + ((1.0 - x2 * x2) / 27.0) * t1,
            "kappa_minus_formula": kappa_q + (t1 / 54.0),
        },
        "theorem_boundary_note": (
            "This sidecar closes the D12 mass-side scalar package numerically on an internal backread continuation surface. "
            "It does not replace the public theorem-grade frontier quark_d12_t1_value_law, does not alter the active builder's "
            "primary-path open payload pair, and does not repair the wrong-sheet CKM boundary."
        ),
        "notes": [
            "The numeric closure uses only the emitted reference-free forward light-quark pair and the explicit continuation assumptions listed in this artifact.",
            "No target masses or CKM data are used to fix the mass-side scalar package on this sidecar surface.",
            "The closed values belong to a continuation-only internal backread surface rather than to the public theorem-grade quark lane.",
            "This sidecar now distinguishes the pure-B source payload pair beta/source_readback from the weighted transport pair tau/Lambda, which depends additionally on the chosen sigma branch.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the D12 quark internal backread continuation closure sidecar.")
    parser.add_argument("--forward-yukawas", default=str(FORWARD_YUKAWAS))
    parser.add_argument("--mass-ray", default=str(MASS_RAY))
    parser.add_argument("--selector-law", default=str(SELECTOR_LAW))
    parser.add_argument("--spread-map", default=str(SPREAD_MAP))
    parser.add_argument("--edge-bridge", default=str(EDGE_BRIDGE))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    spread_map_path = Path(args.spread_map)
    spread_map = _load_json(spread_map_path) if spread_map_path.exists() else None
    edge_bridge_path = Path(args.edge_bridge)
    edge_bridge = _load_json(edge_bridge_path) if edge_bridge_path.exists() else None
    payload = build_payload(
        _load_json(Path(args.forward_yukawas)),
        _load_json(Path(args.mass_ray)),
        _load_json(Path(args.selector_law)),
        spread_map=spread_map,
        edge_bridge=edge_bridge,
    )
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
