#!/usr/bin/env python3
"""
Regression checks for the paper-driven D10/D11 implementation.

These tests intentionally validate two separate things:

1. The literal D10 closure matches the numerical values printed in the paper.
2. The literal D11 appendix transport stays distinct from the stronger
   supplement-backed paper claims until the missing matching layer is
   implemented explicitly.
"""

from __future__ import annotations

import importlib.util
import math
import pathlib
import sys

CORE_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))

MODULE_PATH = str(
    (CORE_DIR / "particle_masses_paper_d10_d11.py")
)


def load_mod():
    spec = importlib.util.spec_from_file_location("pm_paper", MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["pm_paper"] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def assert_close(name: str, actual: float, expected: float, rel_tol: float) -> None:
    rel_err = actual / expected - 1.0
    print(
        f"{name:18s} actual={actual:.10g} expected={expected:.10g} "
        f"rel_err={rel_err:+.3e} tol={rel_tol:.1e}"
    )
    if not math.isclose(actual, expected, rel_tol=rel_tol, abs_tol=0.0):
        raise AssertionError(f"{name} mismatch: actual={actual}, expected={expected}")


def main() -> None:
    mod = load_mod()
    d10 = mod.build_paper_d10()
    d11 = mod.integrate_d11_literal_core(d10)
    supplement = mod.infer_supplement_reconstruction(d10)

    # D10 matches the synchronized paper tables.
    assert_close("alpha_u", d10.alpha_u, 0.04112498, 1e-6)
    assert_close("mz_run", d10.mz_run, 91.65246029, 1e-8)
    assert_close("v", d10.v, 246.7671173, 1e-8)
    assert_close("alpha1_mz", d10.alpha1_mz, 0.01688600178, 1e-8)
    assert_close("alpha2_mz", d10.alpha2_mz, 0.0337784363, 1e-8)
    assert_close("alpha3_mz", d10.alpha3_mz, 0.1183372289, 1e-8)

    # Literal appendix transport with corrected hypercharge normalization.
    assert_close("g_y_u", d11.g_y_u, 0.4481750697, 1e-8)
    assert_close("y_t_u", d11.y_t_u, 0.3898957129, 1e-8)
    assert_close("mt_ms", d11.mt_ms, 154.8871187, 1e-8)
    assert_close("mt_pole", d11.mt_pole, 164.2450878, 1e-8)
    assert_close("m_h_tree", d11.m_h_tree, 115.1813150, 1e-8)

    # Guardrail: the literal appendix path is not the same as the published
    # D11 claim set. If these gaps disappear, the matching layer has changed
    # and the test should be revisited intentionally.
    if (d11.mt_pole - mod.PAPER_D11_TARGETS["mt_pole"]) >= -6.0:
        raise AssertionError("literal D11 mt_pole unexpectedly close to paper claim")
    if (d11.m_h_tree - mod.PAPER_D11_TARGETS["m_h"]) >= -10.0:
        raise AssertionError("literal D11 m_H unexpectedly close to paper claim")

    # Inferred supplement reconstruction:
    # an explicit UV-synchronized transport brings the core close enough that
    # only order-one GeV matching corrections remain.
    assert_close("supp_mt_rec", supplement.reconstructed_mt_pole, mod.PAPER_D11_TARGETS["mt_pole"], 1e-12)
    assert_close("supp_mH_rec", supplement.reconstructed_m_h, mod.PAPER_D11_TARGETS["m_h"], 1e-12)
    if not (5.0e11 <= supplement.transport_switch_scale <= 1.0e12):
        raise AssertionError("inferred UV synchronization scale left the expected 10^12-ish window")
    if abs(supplement.core_mt_pole - 170.26) > 0.15:
        raise AssertionError("supplement core top mass drifted away from the reconstructed branch")
    if abs(supplement.core_m_h - 126.62) > 0.15:
        raise AssertionError("supplement core Higgs mass drifted away from the reconstructed branch")
    if abs(supplement.delta_mt_pole_match) > 2.0:
        raise AssertionError("top matching correction left the stated order-one GeV range")
    if abs(supplement.delta_m_h_match) > 1.0:
        raise AssertionError("higgs matching correction left the stated sub-GeV to GeV range")

    print("\nPaper-driven D10/D11 checks passed.")


if __name__ == "__main__":
    main()
