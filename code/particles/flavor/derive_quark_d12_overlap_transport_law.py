#!/usr/bin/env python3
"""Expose the one-scalar D12 overlap transport law for the quark pure-B branch.

Chain role: collapse the D12 continuation `u/d` pure-B payload pair to one scalar
`Delta_ud_overlap` once the emitted spread totals `(sigma_u, sigma_d)` are fixed.

Mathematics: on the one-scalar D12 continuation family, the odd transport pair
is affine in `Delta_ud_overlap` with coefficients set exactly by the already
emitted spread totals:
`tau_u = sigma_d * Delta / (2 (sigma_u + sigma_d))`,
`tau_d = sigma_u * Delta / (2 (sigma_u + sigma_d))`,
`Lambda = sigma_u sigma_d * Delta / (2 (sigma_u + sigma_d))`.

OPH-derived inputs: the closed quark spread map and the current D12 continuation
mass-branch artifact.

Output: a smaller D12 continuation primitive showing that, on any fixed sigma
branch, the remaining D12 mass-side scalar is `Delta_ud_overlap`, not an
unconstrained tau-pair.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SPREAD_MAP_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_spread_map.json"
D12_BRANCH_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_d12_mass_branch_and_ckm_residual.json"
EDGE_BRIDGE_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_edge_statistics_spread_candidate.json"
SOURCE_PAYLOAD_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_d12_internal_backread_source_payload.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "flavor" / "quark_d12_overlap_transport_law.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _evaluate_branch(delta_value: float, sigma_u: float, sigma_d: float) -> dict[str, float]:
    denom = 2.0 * (sigma_u + sigma_d)
    tau_u = sigma_d * delta_value / denom
    tau_d = sigma_u * delta_value / denom
    lam = sigma_u * sigma_d * delta_value / denom
    return {
        "Delta_ud_overlap": float(delta_value),
        "tau_u_log_per_side": float(tau_u),
        "tau_d_log_per_side": float(tau_d),
        "Lambda_ud_B_transport": float(lam),
        "tau_sum_half_delta_identity": float((tau_u + tau_d) - (0.5 * delta_value)),
        "tau_ratio_minus_sigma_ratio": float((tau_d / tau_u) - (sigma_u / sigma_d)),
        "lambda_minus_sigma_u_tau_u": float(lam - sigma_u * tau_u),
        "lambda_minus_sigma_d_tau_d": float(lam - sigma_d * tau_d),
    }


def _build_sigma_branch(
    *,
    provider_artifact: str | None,
    provider_status: str | None,
    sigma_source_kind: str | None,
    sigma_u: float,
    sigma_d: float,
    sample_delta: float,
    comparison_delta: float,
    internal_backread_delta: float | None,
) -> dict[str, Any]:
    branch = {
        "provider_artifact": provider_artifact,
        "provider_status": provider_status,
        "sigma_source_kind": sigma_source_kind,
        "sigma_u_total_log_per_side": float(sigma_u),
        "sigma_d_total_log_per_side": float(sigma_d),
        "transport_formulas": {
            "tau_u_log_per_side": "sigma_d_total_log_per_side * Delta_ud_overlap / (2 * (sigma_u_total_log_per_side + sigma_d_total_log_per_side))",
            "tau_d_log_per_side": "sigma_u_total_log_per_side * Delta_ud_overlap / (2 * (sigma_u_total_log_per_side + sigma_d_total_log_per_side))",
            "Lambda_ud_B_transport": "sigma_u_total_log_per_side * sigma_d_total_log_per_side * Delta_ud_overlap / (2 * (sigma_u_total_log_per_side + sigma_d_total_log_per_side))",
            "tau_u_plus_tau_d": "Delta_ud_overlap / 2",
            "tau_d_over_tau_u": "sigma_u_total_log_per_side / sigma_d_total_log_per_side",
            "Lambda_from_tau_u": "sigma_u_total_log_per_side * tau_u_log_per_side",
            "Lambda_from_tau_d": "sigma_d_total_log_per_side * tau_d_log_per_side",
        },
        "sample_same_family_point": _evaluate_branch(sample_delta, sigma_u, sigma_d),
        "comparison_only_best_same_family_point": _evaluate_branch(comparison_delta, sigma_u, sigma_d),
    }
    if internal_backread_delta is not None:
        branch["internal_backread_realization"] = _evaluate_branch(internal_backread_delta, sigma_u, sigma_d)
    return branch


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the D12 quark overlap transport law artifact.")
    parser.add_argument("--spread-map", default=str(SPREAD_MAP_JSON))
    parser.add_argument("--d12-branch", default=str(D12_BRANCH_JSON))
    parser.add_argument("--edge-bridge", default=str(EDGE_BRIDGE_JSON))
    parser.add_argument("--source-payload", default=str(SOURCE_PAYLOAD_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    spread_map = _load_json(Path(args.spread_map))
    d12_branch = _load_json(Path(args.d12_branch))
    edge_bridge_path = Path(args.edge_bridge)
    edge_bridge = _load_json(edge_bridge_path) if edge_bridge_path.exists() else None
    source_payload_path = Path(args.source_payload)
    source_payload = _load_json(source_payload_path) if source_payload_path.exists() else None

    sample_delta = float(d12_branch["sample_same_family_point"]["Delta_ud_overlap"])
    comparison_only_best_delta = float(d12_branch["comparison_only_best_same_family_point"]["Delta_ud_overlap"])
    internal_backread_delta = None if source_payload is None else float(source_payload["Delta_ud_overlap"])

    sigma_u = float(spread_map["sigma_u_total_log_per_side"])
    sigma_d = float(spread_map["sigma_d_total_log_per_side"])
    main_builder_branch = _build_sigma_branch(
        provider_artifact=spread_map.get("artifact"),
        provider_status=spread_map.get("spread_emitter_status"),
        sigma_source_kind=spread_map.get("sigma_source_kind"),
        sigma_u=sigma_u,
        sigma_d=sigma_d,
        sample_delta=sample_delta,
        comparison_delta=comparison_only_best_delta,
        internal_backread_delta=internal_backread_delta,
    )

    edge_branch = None
    if edge_bridge is not None:
        edge_sigma_u = float(edge_bridge["candidate_sigmas"]["sigma_u_total_log_per_side"])
        edge_sigma_d = float(edge_bridge["candidate_sigmas"]["sigma_d_total_log_per_side"])
        edge_branch = _build_sigma_branch(
            provider_artifact=edge_bridge.get("artifact"),
            provider_status=edge_bridge.get("bridge_status"),
            sigma_source_kind=edge_bridge.get("candidate_kind"),
            sigma_u=edge_sigma_u,
            sigma_d=edge_sigma_d,
            sample_delta=sample_delta,
            comparison_delta=comparison_only_best_delta,
            internal_backread_delta=internal_backread_delta,
        )

    artifact = {
        "artifact": "oph_quark_d12_overlap_transport_law",
        "generated_utc": _timestamp(),
        "status": "closed_exact_transport_reduction",
        "theorem_tier": "D12_continuation_only",
        "proof_status": "one_scalar_transport_law_closed_given_sigma_branch",
        "strictly_smaller_than": "source_readback_u_log_per_side_and_source_readback_d_log_per_side",
        "next_single_residual_object": "Delta_ud_overlap",
        "input_kind": "fixed_sigma_branch_plus_emitted_same_family_mass_ray",
        "selector_scalar_name": "Delta_ud_overlap",
        "exact_transport_contract": {
            "law_statement": (
                "On any fixed ordered-family sigma branch with positive totals "
                "(sigma_u_total_log_per_side, sigma_d_total_log_per_side), the D12 pure-B transport pair is "
                "not free. It is an exact affine readback of the single selector scalar Delta_ud_overlap."
            ),
            "given_any_fixed_sigma_branch": {
                "tau_u_log_per_side": "sigma_d_total_log_per_side * Delta_ud_overlap / (2 * (sigma_u_total_log_per_side + sigma_d_total_log_per_side))",
                "tau_d_log_per_side": "sigma_u_total_log_per_side * Delta_ud_overlap / (2 * (sigma_u_total_log_per_side + sigma_d_total_log_per_side))",
                "Lambda_ud_B_transport": "sigma_u_total_log_per_side * sigma_d_total_log_per_side * Delta_ud_overlap / (2 * (sigma_u_total_log_per_side + sigma_d_total_log_per_side))",
            },
            "closed_identities": {
                "tau_u_plus_tau_d": "Delta_ud_overlap / 2",
                "tau_d_over_tau_u": "sigma_u_total_log_per_side / sigma_d_total_log_per_side",
                "Lambda_from_tau_u": "sigma_u_total_log_per_side * tau_u_log_per_side",
                "Lambda_from_tau_d": "sigma_d_total_log_per_side * tau_d_log_per_side",
            },
            "transport_side_closed": True,
            "single_residual_object_on_each_fixed_sigma_branch": "Delta_ud_overlap",
        },
        "spread_totals": {
            "sigma_u_total_log_per_side": sigma_u,
            "sigma_d_total_log_per_side": sigma_d,
        },
        "transport_formulas": main_builder_branch["transport_formulas"],
        "sample_same_family_point": main_builder_branch["sample_same_family_point"],
        "comparison_only_best_same_family_point": main_builder_branch["comparison_only_best_same_family_point"],
        "internal_backread_realization": main_builder_branch.get("internal_backread_realization"),
        "sigma_branch_contracts": {
            "main_builder_sigma_pair": main_builder_branch,
            "edge_statistics_bridge_sigma_pair": edge_branch,
        },
        "reduced_exact_gap": {
            "transport_side_closed_given_sigma_branch": True,
            "remaining_scalar_on_any_fixed_sigma_branch": "Delta_ud_overlap",
            "remaining_sigma_gap_for_edge_bridge_branch": (
                None
                if edge_branch is None
                else "promote oph_quark_edge_statistics_spread_candidate from candidate sigma pair to theorem-grade sigma pair"
            ),
        },
        "notes": [
            "On the D12 one-scalar overlap family, the odd quark transport pair is not free once a sigma branch is fixed.",
            "The transport side is therefore algebraically closed: the remaining D12 mass-side scalar on each fixed sigma branch is Delta_ud_overlap, with tau_u, tau_d, and Lambda all determined affinely from it.",
            "The retained numerical same-family points still inherit their Delta_ud_overlap values from sample or compare-only branch points unless an explicit internal-backread source payload is supplied.",
            "This does not close the intrinsic D12 scale law that would single out a unique theorem-grade value on the ray, and it does not by itself promote a candidate sigma branch to theorem status.",
        ],
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
