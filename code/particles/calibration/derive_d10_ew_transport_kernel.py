#!/usr/bin/env python3
"""Export the current D10 pole/effective transport-kernel boundary artifact."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT /  "runs" / "calibration" / "d10_ew_observable_family.json"
DEFAULT_OUT = ROOT /  "runs" / "calibration" / "d10_ew_transport_kernel.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_artifact(family: dict[str, object]) -> dict[str, object]:
    core_source = dict(family.get("core_source", {}))
    generator_keys = list(family.get("generator_keys_unrounded", []))
    coherence_witness = dict(family.get("coherence_witness", {}))
    shared_source = {
        "family_source_id": "d10_running_tree",
        "scheme_id": "freeze_once",
        "origin_kernel_id": "EWTransportKernel_D10",
    }
    return {
        "artifact": "oph_d10_ew_transport_kernel",
        "generated_utc": _timestamp(),
        "kernel_id": "EWTransportKernel_D10",
        "active_readout_selector_candidate_id": "EWActiveReadoutSelector_D10",
        "active_readout_selector_status": "candidate_only",
        "post_selector_missing_object": "EWSharedScalarReadoutMap_D10",
        "shared_scalar_readout_map_status": "candidate_only",
        "next_live_mover": "coherent_pole_effective_readout_object",
        "readout_coherence_clause_id": "EWTransportReadoutCoherence_D10",
        "family_source_artifact": str(family.get("artifact")),
        "family_source_id": str(family.get("observable_family_id")),
        "observable_family_id": "d10_pole_effective",
        "scheme_id": "freeze_once",
        "observable_quartet": ["W", "Z", "alpha_em", "sin2w"],
        "core_source_ref": {
            "generator_keys_unrounded": generator_keys,
            "generator_values_unrounded": core_source,
        },
        "neutral_transport": {
            "basis": ["A", "Z"],
            "entries": ["Pi_AA", "Pi_AZ", "Pi_ZZ"],
            "proof_status": "candidate_only",
        },
        "charged_transport": {
            "basis": ["W"],
            "entries": ["Pi_WW"],
            "proof_status": "candidate_only",
        },
        "derived_readouts": {
            "delta_alpha_from": ["Pi_AA", "Pi_AZ"],
            "delta_kappa_from": ["Pi_AA", "Pi_AZ", "Pi_ZZ"],
            "delta_rho_from": ["Pi_WW", "Pi_ZZ"],
            "delta_rW_from": ["Pi_WW", "Pi_AA", "Pi_AZ", "Pi_ZZ"],
        },
        "reported_outputs": {
            "MW_pole": "derived",
            "MZ_pole": "derived",
            "alpha_em_eff_inv": "derived",
            "sin2w_eff": "derived",
            "v_report": {
                "kind": "inherit_running_core",
            },
        },
        "readout_assignments": {
            "MW_pole": {
                "origin_kernel_id": "EWTransportKernel_D10",
                "via": ["delta_rW", "delta_rho"],
            },
            "MZ_pole": {
                "origin_kernel_id": "EWTransportKernel_D10",
                "via": ["delta_rho"],
            },
            "alpha_em_eff_inv": {
                "origin_kernel_id": "EWTransportKernel_D10",
                "via": ["delta_alpha"],
            },
            "sin2w_eff": {
                "origin_kernel_id": "EWTransportKernel_D10",
                "via": ["delta_kappa"],
            },
            "v_report": {
                "kind": "inherit_running_core",
            },
        },
        "active_readout_family_id": "d10_running_tree",
        "active_readout_reason": "fallback_until_common_readout_certified",
        "selector_rule": {
            "if_common_readout_certified": "d10_pole_effective",
            "if_not_common_readout_certified": "d10_running_tree",
        },
        "coherent_quintet_when_running_family": {
            "W": family.get("mW_run"),
            "Z": family.get("mZ_run"),
            "alpha_em_inv": family.get("alpha_em_inv_mz"),
            "sin2w": family.get("sin2w_mz"),
            "v": family.get("v"),
        },
        "quartet_source_lock": {
            "W": "d10_running_tree",
            "Z": "d10_running_tree",
            "alpha_em": "d10_running_tree",
            "sin2w": "d10_running_tree",
            "v": "d10_running_tree",
        },
        "provenance_equality_fields": [
            "family_source_id",
            "scheme_id",
            "origin_kernel_id",
        ],
        "scalar_provenance": {
            "delta_alpha": dict(shared_source),
            "delta_kappa": dict(shared_source),
            "delta_rho": dict(shared_source),
            "delta_rW": dict(shared_source),
        },
        "family_purity_gate": {
            "no_run_pole_mix": True,
            "z_only_surrogate_forbidden": True,
            "orphan_scalar_corrections_forbidden": True,
            "independently_rounded_targets_forbidden": True,
            "common_readout_certified": False,
        },
        "common_provenance_witness": {
            "all_equal_family_source_id": True,
            "all_equal_scheme_id": True,
            "all_equal_origin_kernel_id": True,
            "shared_source": dict(shared_source),
        },
        "coherence_witness": {
            "running_mass_ratio_residual": coherence_witness.get("running_mass_ratio_residual"),
            "stage3_mass_ratio_residual": coherence_witness.get("stage3_mass_ratio_residual"),
            "mixed_sources_detected": coherence_witness.get("mixed_sources_detected", False),
        },
        "promotion_gate": {
            "mixed_scheme": False,
            "z_only_surrogate_forbidden": True,
            "provenance_equality_required": True,
            "independently_rounded_targets_forbidden": True,
            "common_readout_certified": False,
            "smaller_exact_missing_clause": "EWTransportReadoutCoherence_D10",
            "strictly_smaller_next_subclause": "EWScalarProvenanceEquality_D10",
        },
        "notes": [
            "This artifact is the exact boundary for any pole/effective electroweak family built on top of the current exact D10 running-family core.",
            "The smallest mass-moving local object is now EWActiveReadoutSelector_D10: until one coherent pole/effective family is certified, the active public quintet should remain the running-family quintet instead of mixing W_run with a Stage-3 Z-only surrogate.",
            "Beyond that selector fallback, the next live mover is one coherent shared scalar readout map beneath EWTransportKernel_D10 rather than another per-observable family split.",
            "The smaller exact missing clause is EWTransportReadoutCoherence_D10: either W, Z, alpha_em, and sin^2(theta_W) all stay on the running family or all move together to one common pole/effective family with one shared kernel and scheme.",
            "Inside that criterion, the strictly smaller exact subclause is EWScalarProvenanceEquality_D10: delta_alpha, delta_kappa, delta_rho, and delta_rW must expose one common family source, one frozen scheme, and one origin kernel.",
            "A singleton Z-only surrogate is formally non-promotable under this artifact.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the D10 electroweak transport-kernel boundary artifact.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    family = json.loads(Path(args.input).read_text(encoding="utf-8"))
    artifact = build_artifact(family)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
