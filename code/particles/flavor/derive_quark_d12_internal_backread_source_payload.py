#!/usr/bin/env python3
"""Emit the missing quark pure-B source payload on the D12 internal backread sidecar.

Chain role: materialize the first data-bearing primitive beneath the odd source
scalar pair once the D12 continuation-only backread surface has fixed the
light-quark selector value.

Mathematics: read back the pure-B payload pair
`source_readback_u_log_per_side`, `source_readback_d_log_per_side` together
with the equivalent scalar pair `J_B_source_u`, `J_B_source_d`.

OPH-derived inputs: the D12 internal backread continuation closure and the
closed light-quark selector law.

Output: one continuation-only source-payload artifact that can be consumed by
dictionary-side sidecars without pretending that the public theorem frontier has
closed.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BACKREAD = ROOT / "particles" / "runs" / "flavor" / "quark_d12_internal_backread_continuation_closure.json"
DEFAULT_SELECTOR = ROOT / "particles" / "runs" / "flavor" / "light_quark_isospin_overlap_defect_selector_law.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "flavor" / "quark_d12_internal_backread_source_payload.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_artifact(backread: dict[str, Any], selector_law: dict[str, Any]) -> dict[str, Any]:
    source = dict(backread["closed_source_side_package"])
    delta = float(backread["closed_mass_side_package"]["Delta_ud_overlap"])
    beta_u = float(source["beta_u_diag_B_source"])
    beta_d = float(source["beta_d_diag_B_source"])
    source_u = [float(value) for value in source["source_readback_u_log_per_side"]]
    source_d = [float(value) for value in source["source_readback_d_log_per_side"]]
    b_ord = [float(value) for value in source["B_ord"]]
    b_norm_sq = float(sum(value * value for value in b_ord))
    j_b_u = float(source.get("J_B_source_u", beta_u))
    j_b_d = float(source.get("J_B_source_d", beta_d))

    return {
        "artifact": "oph_quark_d12_internal_backread_source_payload",
        "generated_utc": _timestamp(),
        "scope": "D12_continuation_internal_backread_only",
        "proof_status": "internal_backread_source_payload_emitted",
        "public_promotion_allowed": False,
        "changes_public_theorem_frontier": False,
        "input_artifacts": {
            "internal_backread_continuation_closure": backread.get("artifact"),
            "light_quark_isospin_selector_law": selector_law.get("artifact"),
        },
        "selector_scalar_name": selector_law.get("selector_scalar_name", "Delta_ud_overlap"),
        "Delta_ud_overlap": delta,
        "B_ord": b_ord,
        "B_ord_norm_sq": b_norm_sq,
        "beta_u_diag_B_source": beta_u,
        "beta_d_diag_B_source": beta_d,
        "J_B_source_u": j_b_u,
        "J_B_source_d": j_b_d,
        "source_readback_u_log_per_side": source_u,
        "source_readback_d_log_per_side": source_d,
        "source_readback_u_log_per_side_formula": selector_law.get(
            "source_readback_u_log_per_side_formula",
            "(Delta_ud_overlap / 2) * B_ord",
        ),
        "source_readback_d_log_per_side_formula": selector_law.get(
            "source_readback_d_log_per_side_formula",
            "(-Delta_ud_overlap / 2) * B_ord",
        ),
        "J_B_source_u_formula": selector_law.get("beta_u_diag_B_source_formula", "Delta_ud_overlap / 2"),
        "J_B_source_d_formula": selector_law.get("beta_d_diag_B_source_formula", "-Delta_ud_overlap / 2"),
        "odd_budget_neutrality_formula": selector_law.get(
            "odd_budget_neutrality_formula",
            "beta_u_diag_B_source + beta_d_diag_B_source = 0",
        ),
        "selector_equivalence_formula": selector_law.get(
            "selector_equivalence_formula",
            "Delta_ud_overlap = beta_u_diag_B_source - beta_d_diag_B_source",
        ),
        "pure_B_certificates": {
            "center_entry_u": float(source_u[1]),
            "center_entry_d": float(source_d[1]),
            "endpoint_sum_u": float(source_u[0] + source_u[2]),
            "endpoint_sum_d": float(source_d[0] + source_d[2]),
            "J_B_from_endpoint_u": float((source_u[2] - source_u[0]) / 2.0),
            "J_B_from_endpoint_d": float((source_d[2] - source_d[0]) / 2.0),
            "dot_u_over_norm": float(sum(u * b for u, b in zip(source_u, b_ord, strict=True)) / b_norm_sq),
            "dot_d_over_norm": float(sum(d * b for d, b in zip(source_d, b_ord, strict=True)) / b_norm_sq),
        },
        "builder_reduction_status": {
            "active_builder_residual_on_primary_path": backread.get("active_builder_residual_on_primary_path"),
            "residual_object_emitted_on_this_sidecar": True,
        },
        "notes": [
            "This artifact is the explicit emitted pure-B payload pair that had remained named but unmaterialized on the main quark builder path.",
            "The payload is continuation-only and internal-backread-only: it does not promote quark_d12_t1_value_law or the public quark theorem surface.",
            "Once emitted, J_B_source_u and J_B_source_d are fixed algebraically by endpoint readback on B_ord.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the quark D12 internal-backread source payload artifact.")
    parser.add_argument("--backread", default=str(DEFAULT_BACKREAD))
    parser.add_argument("--selector", default=str(DEFAULT_SELECTOR))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    backread = json.loads(Path(args.backread).read_text(encoding="utf-8"))
    selector_law = json.loads(Path(args.selector).read_text(encoding="utf-8"))
    artifact = build_artifact(backread, selector_law)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
