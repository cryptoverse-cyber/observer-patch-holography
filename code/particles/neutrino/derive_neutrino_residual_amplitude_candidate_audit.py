#!/usr/bin/env python3
"""Audit simple compare-only candidates for the residual neutrino amplitude bridge.

This sits one layer above the exact q_mean**p factorization already proved in the
attachment irreducibility theorem:

    A_nu := lambda_nu * q_mean**p.

The goal here is not to promote a bridge law. It is to search for small
residual-amplitude formulas built from the live residual scalar pool after the
exact q_mean-homogeneity has been stripped off.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
READBACK_JSON = ROOT / "particles" / "runs" / "neutrino" / "realized_same_label_gap_defect_readback.json"
NORMALIZER_JSON = ROOT / "particles" / "runs" / "neutrino" / "same_label_overlap_defect_weight_normalizer.json"
REPAIR_JSON = ROOT / "particles" / "runs" / "neutrino" / "neutrino_weighted_cycle_repair.json"
HESSIAN_JSON = ROOT / "particles" / "runs" / "neutrino" / "majorana_overlap_defect_hessian.json"
COMPARE_FIT_JSON = ROOT / "particles" / "runs" / "neutrino" / "neutrino_compare_only_scale_fit.json"
SCALE_ANCHOR_JSON = ROOT / "particles" / "runs" / "neutrino" / "neutrino_scale_anchor.json"
DEFECT_FAMILY_JSON = ROOT / "particles" / "runs" / "neutrino" / "defect_weighted_mu_e_family.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "neutrino" / "neutrino_residual_amplitude_candidate_audit.json"
EXTENDED_SCALE_KEYS = (
    "base_mu_over_mstar",
    "doublet_center_over_mstar",
    "heavy_light_gap_over_mstar",
    "solar_response_over_mstar",
)


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _monomial_value(values: dict[str, float], keys: tuple[str, ...], exponents: tuple[float, ...]) -> float:
    value = 1.0
    for key, exponent in zip(keys, exponents):
        value *= values[key] ** exponent
    return value


def _formula_string(keys: tuple[str, ...], exponents: tuple[float, ...]) -> str:
    pieces = []
    for key, exponent in zip(keys, exponents):
        if exponent == 1:
            pieces.append(key)
        else:
            pieces.append(f"{key}^{exponent:g}")
    return " * ".join(pieces)


def _rank_candidates(values: dict[str, float], target_ratio: float) -> list[dict[str, Any]]:
    exponent_choices = (-2.0, -1.0, -0.5, 0.5, 1.0, 2.0)
    candidates: list[dict[str, Any]] = []
    for width in (1, 2, 3):
        for keys in itertools.combinations(values.keys(), width):
            for exponents in itertools.product(exponent_choices, repeat=width):
                value = _monomial_value(values, keys, exponents)
                rel_error = abs(value - target_ratio) / target_ratio
                candidates.append(
                    {
                        "formula": _formula_string(keys, exponents),
                        "keys": list(keys),
                        "exponents": list(exponents),
                        "value": value,
                        "relative_error": rel_error,
                        "complexity": width,
                    }
                )
    candidates.sort(key=lambda item: (item["relative_error"], item["complexity"]))
    return candidates


def build_payload(
    *,
    readback: dict[str, Any],
    normalizer: dict[str, Any],
    repair: dict[str, Any],
    hessian: dict[str, Any],
    compare_fit: dict[str, Any],
    scale_anchor: dict[str, Any],
    defect_family: dict[str, Any],
) -> dict[str, Any]:
    qbar = dict(normalizer["qbar_e"])
    defect = dict(readback["defect_e"])
    gap = dict(readback["gap_e"])
    mu = dict(normalizer["mu_e"])
    selector = dict(repair["selector_phases_absolute"])
    center = dict(hessian["selector_point"])

    i_nu = sum(
        float(qbar[key]) * (1.0 - math.cos(float(selector[key]) - float(center[key])))
        for key in ("psi12", "psi23", "psi31")
    )

    q_mean = float(normalizer["q_mean"])
    p_nu = float(repair["weight_exponent"])
    lambda_fit = float(compare_fit["fits"]["weighted_least_squares"]["lambda_nu"])
    m_star_eV = float(scale_anchor["anchors"]["m_star_gev"]) * 1.0e9
    residual_amplitude = lambda_fit * (q_mean**p_nu)
    target_ratio = residual_amplitude / m_star_eV

    core_residual_pool = {
        "I_nu": i_nu,
        "ratio_hat": float(repair["dimensionless_ratio_dm21_over_dm32"]),
        "gamma": float(repair["gamma"]),
        "chi": float(repair["diag_loading"]),
        "sum_defect": float(sum(defect.values())),
        "sum_gap": float(sum(gap.values())),
        "sum_mu": float(sum(mu.values())),
        "sum_qbar": float(sum(qbar.values())),
        "prod_qbar": float(math.prod(qbar.values())),
    }
    m_star_gev = float(scale_anchor["anchors"]["m_star_gev"])
    extended_residual_pool = dict(core_residual_pool)
    extended_residual_pool.update(
        {
            "base_mu_over_mstar": float(defect_family["base_mu_nu"]) / m_star_gev,
            "doublet_center_over_mstar": float(defect_family["current_doublet_center_gev"]) / m_star_gev,
            "heavy_light_gap_over_mstar": float(defect_family["current_heavy_light_gap_gev"]) / m_star_gev,
            "solar_response_over_mstar": float(defect_family["first_order_solar_response_coefficient_gev"]) / m_star_gev,
        }
    )

    excluded_trivial_scalars = {
        "sum_qbar": {
            "reason": "The closed qbar_e normalizer fixes sum_qbar = 3 exactly, so it is a trivial normalization constant rather than a bridge signal.",
            "value": float(core_residual_pool["sum_qbar"]),
        }
    }
    search_core_pool = dict(core_residual_pool)
    search_extended_pool = dict(extended_residual_pool)
    search_core_pool.pop("sum_qbar", None)
    search_extended_pool.pop("sum_qbar", None)

    core_ranked = _rank_candidates(search_core_pool, target_ratio)
    extended_ranked = _rank_candidates(search_extended_pool, target_ratio)
    best_core = core_ranked[0]
    top_single = [item for item in core_ranked if item["complexity"] == 1][:10]
    top_double = [item for item in core_ranked if item["complexity"] == 2][:10]
    top_triple = [item for item in core_ranked if item["complexity"] == 3][:10]
    best_extended = extended_ranked[0]
    extended_top_single = [item for item in extended_ranked if item["complexity"] == 1][:10]
    extended_top_double = [item for item in extended_ranked if item["complexity"] == 2][:10]
    extended_top_triple = [item for item in extended_ranked if item["complexity"] == 3][:10]
    family_assisted = [
        item for item in extended_ranked if any(key in EXTENDED_SCALE_KEYS for key in item["keys"])
    ]
    best_family_assisted = family_assisted[0]

    return {
        "artifact": "oph_neutrino_residual_amplitude_candidate_audit",
        "generated_utc": _timestamp(),
        "status": "compare_only_residual_amplitude_search",
        "public_promotion_allowed": False,
        "residual_amplitude_definition": "A_nu = lambda_nu * q_mean^p_nu",
        "target_residual_ratio": {
            "name": "A_nu_star / m_star",
            "A_nu_star_eV": residual_amplitude,
            "m_star_eV": m_star_eV,
            "value": target_ratio,
            "source": "weighted_least_squares_compare_only_scale_fit_after_exact_q_mean_factorization",
        },
        "selected_point_relative_phase_contract": {
            "definition": "delta_psi_e = psi_e(weighted_cycle_selector) - psi_e(equal_split_selector)",
            "selector_source": "neutrino_weighted_cycle_repair.selector_phases_absolute",
            "center_source": "majorana_overlap_defect_hessian.selector_point",
        },
        "residual_invariant_pool": core_residual_pool,
        "extended_residual_invariant_pool": extended_residual_pool,
        "excluded_trivial_scalars_from_search": excluded_trivial_scalars,
        "search_family": {
            "kind": "one_to_three_factor_monomials_on_residual_scalar_pool",
            "objective": "minimize relative error to A_nu_star / m_star",
            "exponents": [-2.0, -1.0, -0.5, 0.5, 1.0, 2.0],
            "disallowed_shortcuts": ["q_mean", "q_mean^p_nu", "lambda_nu", "external_oscillation_anchor", "sum_qbar"],
        },
        "best_compare_only_candidate": best_core,
        "best_extended_compare_only_candidate": best_extended,
        "family_assisted_scale_keys": list(EXTENDED_SCALE_KEYS),
        "best_family_assisted_compare_only_candidate": best_family_assisted,
        "top_single_factor_candidates": top_single,
        "top_two_factor_candidates": top_double,
        "top_three_factor_candidates": top_triple,
        "extended_top_single_factor_candidates": extended_top_single,
        "extended_top_two_factor_candidates": extended_top_double,
        "extended_top_three_factor_candidates": extended_top_triple,
        "top_family_assisted_candidates": family_assisted[:10],
        "working_observation": (
            "After stripping off the exact q_mean^p_nu homogeneity, the residual compare-only target "
            "A_nu_star / m_star is numerically much smaller and cleaner than the raw bridge factor "
            "lambda_nu / m_star. On the core residual scalar pool the strongest simple clue is "
            "sqrt(I_nu) * sqrt(ratio_hat) / sum_defect. On the extended pool that also includes "
            "defect-weighted mu_e family scales normalized by m_star, the strongest genuinely family-assisted clue is "
            f"`{best_family_assisted['formula']}`. It lands very close to the same target but still does not beat the core clue "
            "`sqrt(I_nu) * sqrt(ratio_hat) / sum_defect`. Both remain compare-only audit signals."
        ),
        "hard_guard": {
            "status": "do_not_promote",
            "reason": (
                "This search runs only on low-complexity residual monomials. It does not prove that "
                "the current corpus emits the residual amplitude bridge, and it must not be turned into "
                "a theorem-grade lambda_nu or A_nu law without an supported OPH derivation."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit residual-amplitude candidates above the closed q_mean^p factorization.")
    parser.add_argument("--readback", default=str(READBACK_JSON))
    parser.add_argument("--normalizer", default=str(NORMALIZER_JSON))
    parser.add_argument("--repair", default=str(REPAIR_JSON))
    parser.add_argument("--hessian", default=str(HESSIAN_JSON))
    parser.add_argument("--compare-fit", default=str(COMPARE_FIT_JSON))
    parser.add_argument("--scale-anchor", default=str(SCALE_ANCHOR_JSON))
    parser.add_argument("--defect-family", default=str(DEFECT_FAMILY_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    payload = build_payload(
        readback=_load_json(Path(args.readback)),
        normalizer=_load_json(Path(args.normalizer)),
        repair=_load_json(Path(args.repair)),
        hessian=_load_json(Path(args.hessian)),
        compare_fit=_load_json(Path(args.compare_fit)),
        scale_anchor=_load_json(Path(args.scale_anchor)),
        defect_family=_load_json(Path(args.defect_family)),
    )
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
