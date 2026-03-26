#!/usr/bin/env python3
"""Export the current charged mean-eigenvalue witness candidate."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT /  "runs" / "flavor" / "charged_budget_transport.json"
DEFAULT_OUT = ROOT /  "runs" / "flavor" / "charged_mean_eigenvalue_certificate.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the charged mean-eigenvalue witness artifact.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    cert = payload["charged_dirac_scalarization_certificate"]
    family_eigenvalues = [float(x) for x in cert.get("family_eigenvalues", [])]
    mean_value = sum(family_eigenvalues) / len(family_eigenvalues) if family_eigenvalues else None
    artifact = {
        "artifact": "charged_common_refinement_mean_eigenvalue_certificate",
        "generated_utc": _timestamp(),
        "parent_candidate": cert.get("candidate_id"),
        "transport_kind": cert.get("transport_kind"),
        "generator_kind": cert.get("generator_kind"),
        "refinement_pair": cert.get("refinement_pair"),
        "mean_formula": "Delta_mean(X,X';rho) = mean(family_eigenvalues(X^rho)) - mean(family_eigenvalues(X'^rho))",
        "current_family_eigenvalues": family_eigenvalues,
        "current_mean_eigenvalue": mean_value,
        "left_common_family_eigenvalues": None,
        "right_common_family_eigenvalues": None,
        "left_common_mean": None,
        "right_common_mean": None,
        "mean_residual": None,
        "gap_side_support_status": cert.get("gap_side_support_status"),
        "seed_formula": cert.get("seed_formula"),
        "seed_defect_formula": cert.get("seed_defect_formula"),
        "sector_equalizer_formula": cert.get("sector_equalizer_formula"),
        "gluing_norm_formula": cert.get("gluing_norm_formula"),
        "sectorwise_collapse_condition": "Delta_mean = 0 with proxy-supported min-gap side",
        "promotion_targets": ["functional_equalizer_closed", "decomposition_independence_status", "proof_status", "g_e", "g_ch"],
        "proof_status": "candidate_only",
        "notes": [
            "This is the smallest live constructive witness beneath charged_common_refinement_sigma_seed_equalizer.",
            "Once the mean witness closes on the same-label common-refinement package, the existing seed-defect law collapses to zero on the current family and the sector gluing norm should vanish.",
        ],
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
