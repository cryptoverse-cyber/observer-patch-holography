#!/usr/bin/env python3
"""Derive the current neutrino capacity-sector anchor from live OPH outputs."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any


ROOT = pathlib.Path(__file__).resolve().parents[1]
PARTICLE_CODE = ROOT / "core"
sys.path.insert(0, str(PARTICLE_CODE))

import oph_predict_compare as opc  # noqa: E402


def build_capacity_sector(P: float, log_dim_H: float, loops: int, mu_u_override: float | None) -> dict[str, Any]:
    pred = opc.build_predictions(
        P=float(P),
        log_dim_H=float(log_dim_H),
        with_hadrons=False,
        np_json=None,
        loops=int(loops),
        hadron_profile="demo",
        hadron_overrides={},
    )
    v = float(pred["v"])
    mu_u = float(mu_u_override if mu_u_override is not None else pred["M_U"])
    m_star_capacity = float(pred["rho_Lambda_1_4"])
    m_star_d10 = (v * v) / mu_u
    collective_mode = [
        [1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0],
        [1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0],
        [1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0],
    ]
    return {
        "inputs": {
            "P": float(P),
            "log_dim_H": float(log_dim_H),
            "loops": int(loops),
            "mu_u_used_gev": mu_u,
        },
        "anchors": {
            "m_star_capacity_gev": m_star_capacity,
            "m_star_d10_v2_over_mu_u_gev": m_star_d10,
            "anchor_ratio_capacity_over_d10": (m_star_capacity / m_star_d10) if m_star_d10 else None,
        },
        "live_predictor_snapshot": {
            "v_gev": v,
            "M_U_gev": float(pred["M_U"]),
            "rho_Lambda_1_4_gev": m_star_capacity,
            "m_nu_e_gev": float(pred["m_nu_e"]),
            "m_nu_mu_gev": float(pred["m_nu_mu"]),
            "m_nu_tau_gev": float(pred["m_nu_tau"]),
        },
        "collective_mode": {
            "basis": "democratic_rank_one",
            "u_vector": [0.5773502691896258, 0.5773502691896258, 0.5773502691896258],
            "u_uT": collective_mode,
        },
        "status": "scale_anchor_only",
        "notes": [
            "This artifact fixes the current scale anchor only.",
            "Family structure, splittings, and mixing require a separate OPH-derived response tensor.",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Derive the current neutrino capacity-sector anchor.")
    ap.add_argument("--P", type=float, default=float(opc.P_DEFAULT))
    ap.add_argument("--log-dim-H", type=float, default=float(opc.LOG_DIM_H_DEFAULT))
    ap.add_argument("--loops", type=int, default=4)
    ap.add_argument("--mu-u-override", type=float, default=None, help="Override M_U when you want to test a different D10 comparison scale.")
    ap.add_argument("--out", default="runs/neutrino/capacity_sector.json")
    args = ap.parse_args()

    out_path = pathlib.Path(args.out)
    if not out_path.is_absolute():
        out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_capacity_sector(args.P, args.log_dim_H, args.loops, args.mu_u_override)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
