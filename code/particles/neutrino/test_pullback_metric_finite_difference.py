#!/usr/bin/env python3
"""Finite-difference the Majorana lift and compare with the exported pullback metric."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_CAPACITY = ROOT /  "runs" / "neutrino" / "capacity_sector.json"
DEFAULT_FAMILY = ROOT /  "runs" / "neutrino" / "family_response_tensor.json"
DEFAULT_PULLBACK = ROOT /  "runs" / "neutrino" / "majorana_phase_pullback_metric.json"


def _lift(m_star: float, e_nu: np.ndarray, n_diag: np.ndarray, coords: np.ndarray) -> np.ndarray:
    psi12, psi23, psi31 = coords.tolist()
    phase = np.ones((3, 3), dtype=complex)
    phase[0, 1] = np.exp(1j * psi12)
    phase[1, 0] = phase[0, 1]
    phase[1, 2] = np.exp(1j * psi23)
    phase[2, 1] = phase[1, 2]
    phase[2, 0] = np.exp(1j * psi31)
    phase[0, 2] = phase[2, 0]
    return m_star * (n_diag @ (e_nu * phase) @ n_diag)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the pullback metric against finite differences.")
    parser.add_argument("--capacity", default=str(DEFAULT_CAPACITY))
    parser.add_argument("--family", default=str(DEFAULT_FAMILY))
    parser.add_argument("--pullback", default=str(DEFAULT_PULLBACK))
    args = parser.parse_args()

    capacity = json.loads(pathlib.Path(args.capacity).read_text(encoding="utf-8"))
    family = json.loads(pathlib.Path(args.family).read_text(encoding="utf-8"))
    pullback = json.loads(pathlib.Path(args.pullback).read_text(encoding="utf-8"))
    if not bool(pullback.get("phase_action_closed", False)):
        print("pullback metric not closed; skip finite-difference test")
        return 0

    m_star = float(capacity["anchors"]["m_star_capacity_gev"])
    e_nu = np.asarray(family["E_nu"], dtype=float)
    n_diag = np.diag(np.asarray(family["majorana_normalization_diag"], dtype=float))
    exported = np.asarray(pullback["pullback_metric_residual_basis_2x2"], dtype=float)
    basis = np.asarray([[1.0, 1.0], [-1.0, 0.0], [0.0, -1.0]], dtype=float)
    eps = 1.0e-7
    jacobian_cols = []
    origin = np.zeros(3, dtype=float)
    for idx in range(2):
        step = basis[:, idx] * eps
        plus = _lift(m_star, e_nu, n_diag, origin + step)
        minus = _lift(m_star, e_nu, n_diag, origin - step)
        jacobian_cols.append(((plus - minus) / (2.0 * eps)).reshape(-1))
    j_mat = np.stack(jacobian_cols, axis=1)
    finite_metric = np.real(np.conj(j_mat).T @ j_mat)
    if not np.allclose(finite_metric, exported, atol=1.0e-15, rtol=1.0e-12):
        print("finite-difference pullback metric mismatch", file=sys.stderr)
        return 1
    print("pullback metric finite-difference check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
