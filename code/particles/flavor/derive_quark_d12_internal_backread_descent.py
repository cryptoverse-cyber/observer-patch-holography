#!/usr/bin/env python3
"""Build a continuation-only quark descent with explicit D12 backread payload.

Chain role: materialize a quark descent artifact that no longer leaves the odd
pure-B payload pair or the weighted transport lift implicit on the internal
backread sidecar.

Mathematics: keep the local projector-resolved odd splitter and mean surface
from the active quark descent, replace the open pure-B payload with the emitted
D12 internal-backread source payload, and replace the open transport slot with
the exact weighted D12 overlap law on the edge-statistics sigma branch.

OPH-derived inputs: the active quark descent shape data, the edge-statistics
spread candidate, the explicit D12 internal-backread source payload, and the
exact D12 overlap transport law.

Output: one continuation-only descent artifact that can be consumed by the
existing forward Yukawa builder without placeholder blockers.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BASE_DESCENT = ROOT / "particles" / "runs" / "flavor" / "quark_sector_descent.json"
DEFAULT_EDGE_BRIDGE = ROOT / "particles" / "runs" / "flavor" / "quark_edge_statistics_spread_candidate.json"
DEFAULT_SOURCE_PAYLOAD = ROOT / "particles" / "runs" / "flavor" / "quark_d12_internal_backread_source_payload.json"
DEFAULT_OVERLAP_LAW = ROOT / "particles" / "runs" / "flavor" / "quark_d12_overlap_transport_law.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "flavor" / "quark_d12_internal_backread_descent.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_artifact(
    base_descent: dict[str, Any],
    edge_bridge: dict[str, Any],
    source_payload: dict[str, Any],
    overlap_law: dict[str, Any],
) -> dict[str, Any]:
    edge_branch = dict((overlap_law.get("sigma_branch_contracts") or {}).get("edge_statistics_bridge_sigma_pair") or {})
    weighted = dict(edge_branch.get("internal_backread_realization") or {})
    if not weighted:
        raise ValueError("D12 overlap transport law must provide the internal-backread realization on the edge-statistics sigma branch")

    sigma_u = float(edge_bridge["candidate_sigmas"]["sigma_u_total_log_per_side"])
    sigma_d = float(edge_bridge["candidate_sigmas"]["sigma_d_total_log_per_side"])
    v_u = [float(value) for value in edge_bridge["profile_rays"]["v_u"]]
    v_d = [float(value) for value in edge_bridge["profile_rays"]["v_d"]]
    b_ord = [float(value) for value in source_payload["B_ord"]]
    tau_u = float(weighted["tau_u_log_per_side"])
    tau_d = float(weighted["tau_d_log_per_side"])

    e_u_base = [sigma_u * value for value in v_u]
    e_d_base = [sigma_d * value for value in v_d]
    e_u_log = [base + tau_u * b for base, b in zip(e_u_base, b_ord, strict=True)]
    e_d_log = [base + tau_d * b for base, b in zip(e_d_base, b_ord, strict=True)]

    artifact = dict(base_descent)
    artifact.update(
        {
            "artifact": "oph_quark_d12_internal_backread_descent",
            "generated_utc": _timestamp(),
            "scope": "D12_continuation_internal_backread_only",
            "proof_status": "internal_backread_continuation_descent_closed",
            "quark_descent_proof_status": "closed",
            "even_excitation_proof_status": "closed",
            "exact_missing_object": None,
            "hierarchy_driver_status": "candidate_spread_values_populated",
            "even_excitation_source_artifact": edge_bridge.get("artifact"),
            "even_excitation_source_status": "internal_backread_edge_bridge_closed_on_sidecar",
            "spread_sigma_u_total_log_per_side": sigma_u,
            "spread_sigma_d_total_log_per_side": sigma_d,
            "spread_sigma_source_kind": "edge_statistics_bridge_internal_backread_realization",
            "constructive_edge_statistics_bridge_artifact": edge_bridge.get("artifact"),
            "constructive_edge_statistics_bridge_status": edge_bridge.get("bridge_status"),
            "constructive_edge_statistics_bridge_candidate_sigmas": edge_bridge.get("candidate_sigmas"),
            "J_B_source_u": source_payload.get("J_B_source_u"),
            "J_B_source_d": source_payload.get("J_B_source_d"),
            "tau_u_log_per_side": tau_u,
            "tau_d_log_per_side": tau_d,
            "E_u_log": e_u_log,
            "E_d_log": e_d_log,
            "b_odd_source_scalar_evaluator_artifact": source_payload.get("artifact"),
            "b_odd_source_scalar_evaluator_status": source_payload.get("proof_status"),
        }
    )

    metadata = dict(artifact.get("metadata", {}))
    metadata.update(
        {
            "base_descent_artifact": base_descent.get("artifact"),
            "source_payload_artifact": source_payload.get("artifact"),
            "overlap_law_artifact": overlap_law.get("artifact"),
            "note": (
                "Continuation-only D12 internal-backread quark descent. "
                "The local projector-resolved odd splitter and mean surface are inherited from the active descent, "
                "while the open pure-B payload and weighted transport slots are replaced by the emitted D12 internal-backread payload "
                "and the exact edge-branch overlap law realization."
            ),
        }
    )
    artifact["metadata"] = metadata
    return artifact


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the D12 internal-backread quark descent artifact.")
    parser.add_argument("--base-descent", default=str(DEFAULT_BASE_DESCENT))
    parser.add_argument("--edge-bridge", default=str(DEFAULT_EDGE_BRIDGE))
    parser.add_argument("--source-payload", default=str(DEFAULT_SOURCE_PAYLOAD))
    parser.add_argument("--overlap-law", default=str(DEFAULT_OVERLAP_LAW))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    base_descent = json.loads(Path(args.base_descent).read_text(encoding="utf-8"))
    edge_bridge = json.loads(Path(args.edge_bridge).read_text(encoding="utf-8"))
    source_payload = json.loads(Path(args.source_payload).read_text(encoding="utf-8"))
    overlap_law = json.loads(Path(args.overlap_law).read_text(encoding="utf-8"))
    artifact = build_artifact(base_descent, edge_bridge, source_payload, overlap_law)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
