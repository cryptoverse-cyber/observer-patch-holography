#!/usr/bin/env python3
"""Export the current D11 common readout-kernel boundary artifact."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT /  "runs" / "calibration" / "d11_critical_surface_readout.json"
DEFAULT_D10_SOURCE = ROOT /  "runs" / "calibration" / "d10_ew_observable_family.json"
DEFAULT_RESULTS_STATUS = ROOT /  "RESULTS_STATUS.md"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_artifact(d10_source: Path, results_status: Path) -> dict[str, object]:
    y_t_core = 0.92046435
    lambda_core = 0.13164915
    delta_y = 0.01156247
    delta_lambda = -0.00294158
    sigma_from_y = delta_y / y_t_core
    kappa_observed = (-delta_lambda / lambda_core) / sigma_from_y
    kappa_candidate = 16.0 / 9.0
    rank_one_residual_abs = abs(sigma_from_y - (-(9.0 / 16.0) * delta_lambda / lambda_core))
    return {
        "artifact": "oph_d11_critical_surface_readout",
        "generated_utc": _timestamp(),
        "d10_source_artifact": str(d10_source),
        "results_status_surface": str(results_status),
        "transport_family": "sm_below_sync__mssm_like_gauge_above_sync",
        "mu_sync_gev": 6.8e11,
        "mu_sync_status": "candidate",
        "mu_eval_gev": 160.61247,
        "core": {
            "mt_ms_gev": 160.61247,
            "mt_pole_core_gev": 170.26125,
            "mH_core_gev": 126.62263,
            "y_t_core_mt": y_t_core,
            "lambda_core_mt": lambda_core,
            "alpha_s_mt": 0.11018777,
            "pole_ratio_core": 1.06007492,
        },
        "readout_kernel": {
            "name": "CriticalSurfaceReadoutKernel_D11",
            "status": "rank_one_candidate",
            "family": "relative_core_ray",
            "seed_symbol": "sigma_D11_HT(mu_t)",
            "seed_value": None,
            "kappa_lambda_over_y": {
                "candidate": kappa_candidate,
                "observed_diagnostic": kappa_observed,
            },
            "delta_y_t_formula": "sigma_D11_HT * y_t_core_mt",
            "delta_lambda_formula": "-kappa_lambda_over_y.candidate * sigma_D11_HT * lambda_core_mt",
            "sigma_from_y_t": sigma_from_y,
            "sigma_from_lambda": -delta_lambda / (kappa_candidate * lambda_core),
            "rank_one_residual_abs": rank_one_residual_abs,
            "common_provenance": None,
            "delta_y_t_mt": None,
            "delta_lambda_mt": None,
        },
        "diagnostic_required_to_current_refs": {
            "ref_surface": str(results_status),
            "ref_mt_pole_gev": 172.4,
            "ref_mH_gev": 125.20,
            "delta_y_t_mt": 0.01156247,
            "delta_lambda_mt": -0.00294158,
            "delta_mt_pole_gev": 2.13875,
            "delta_mH_gev": -1.42263,
        },
        "jacobian": {
            "d_mt_pole_d_y_t": 184.97,
            "d_mH_d_lambda": 480.0,
        },
        "predicted": {
            "mt_pole_gev": None,
            "mH_gev": None,
        },
        "exact_missing_object": "CriticalSurfaceReadoutKernel_D11",
        "readout_vector_symbol": "Theta_D11_HT(mu_t) = (delta_y_t(mu_t), delta_lambda(mu_t))",
        "closure_state": "open_until_common_readout_kernel_closed",
        "notes": [
            "The synchronized D11 core already captures most of the numerical gain over the literal appendix flow, but mu_sync alone moves top and Higgs together and cannot do the needed top-up / Higgs-down move.",
            "The smallest constructive D11 object is a common low-scale readout vector Theta_D11_HT(mu_t) = (delta_y_t, delta_lambda) produced by one CriticalSurfaceReadoutKernel_D11, not two independent per-observable residual fits.",
            "The current diagnostic vector already lies almost exactly on a rank-one relative-core ray with kappa_HT = 16/9, so the remaining irreducible live object is the shared scalar seed sigma_D11_HT rather than a free two-component readout.",
            "Until that common readout kernel closes, the honest D11 surface is the synchronized core plus one explicit shared readout-kernel burden.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the D11 critical-surface readout boundary artifact.")
    parser.add_argument("--d10-source", default=str(DEFAULT_D10_SOURCE))
    parser.add_argument("--results-status", default=str(DEFAULT_RESULTS_STATUS))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    artifact = build_artifact(Path(args.d10_source), Path(args.results_status))
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
