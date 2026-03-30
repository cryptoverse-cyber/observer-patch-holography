#!/usr/bin/env python3
"""Emit the charged absolute-anchor extension scaffold.

This is not a closure theorem. It records the exact contract the future
theorem-grade affine-covariant charged anchor ``A_ch`` must satisfy once the
upstream charged operator candidate is promoted.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
UNDERDETERMINATION_JSON = (
    ROOT / "particles" / "runs" / "leptons" / "charged_absolute_scale_underdetermination_theorem.json"
)
AUDIT_JSON = ROOT / "particles" / "runs" / "leptons" / "lepton_current_family_exactness_audit.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "leptons" / "charged_absolute_anchor_section.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the charged absolute-anchor section scaffold.")
    parser.add_argument("--underdetermination", default=str(UNDERDETERMINATION_JSON))
    parser.add_argument("--audit", default=str(AUDIT_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    underdetermination = _load_json(Path(args.underdetermination))
    audit = _load_json(Path(args.audit))

    artifact = {
        "artifact": "oph_charged_absolute_anchor_section",
        "generated_utc": _timestamp(),
        "status": "missing_theorem_side_breaker",
        "public_promotion_allowed": False,
        "exact_missing_object": "charged_absolute_anchor_A_ch",
        "section_kind": "common_shift_torsor_section",
        "current_surface": "charged_shape_only_common_shift_quotient",
        "upstream_prerequisite": {
            "required_theorem": "oph_generation_bundle_branch_generator_splitting",
            "required_clause": "compression_descendant_commutator_vanishes_or_is_uniformly_quadratic_small_after_central_split",
            "current_status": audit.get("exact_waiting_set", {}),
        },
        "input_contract": {
            "must_use": [
                "theorem-grade charged sector-response artifact after C_hat_e promotion",
                "lepton_current_family_exactness_audit.json",
            ],
            "must_not_use": [
                "measured charged masses",
                "compare-only D12 continuation targets",
                "PMNS or CKM target fits",
                "shared-budget seed alone",
                "centered-shape-only functionals",
            ],
        },
        "covariance_contract": "A_ch(logm + c*(1,1,1)) = A_ch(logm) + c",
        "required_new_scalar": "A_ch",
        "derived_quantities_on_fill": {
            "g_e": "exp(A_ch)",
            "Delta_e_abs": "log(g_ch_shared) - A_ch",
        },
        "hard_rejections": {
            "common_shift_invariant_functionals": "cannot emit A_ch because they satisfy F(logm + c*(1,1,1)) = F(logm)",
            "gamma_min_restore_pick": {
                "g_e": 0.6822819838027987,
                "Delta_e_abs": 0.30236566025890826,
                "status": "invalid_orbit_pick",
            },
            "d12_compare_only_target": {
                "g_e_star": underdetermination["compare_only_continuation_target"]["g_e_star"],
                "Delta_e_abs_star": underdetermination["compare_only_continuation_target"]["delta_e_abs_star"],
                "status": "compare_only_not_theorem",
            },
        },
        "notes": [
            "This scaffold exists to package the exact future contract for the charged absolute anchor.",
            "Promotion of C_hat_e^cand is upstream and necessary, but not sufficient: it promotes theorem-grade centered data, not the affine common-shift breaker itself.",
            "Any candidate A_ch must exhibit the affine +c covariance explicitly, not merely reproduce one preferred numerical representative.",
        ],
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
