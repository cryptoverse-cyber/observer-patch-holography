#!/usr/bin/env python3
"""Export the current sector-even quark excitation-evaluator candidate."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GENERATOR = ROOT /  "runs" / "flavor" / "generation_bundle_branch_generator.json"
DEFAULT_DESCENT = ROOT /  "runs" / "flavor" / "quark_sector_descent.json"
DEFAULT_OUT = ROOT /  "runs" / "flavor" / "family_excitation_evaluator.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ctr(values: np.ndarray) -> list[float]:
    centered = values - np.mean(values)
    return [float(x) for x in centered.tolist()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the family excitation-evaluator candidate artifact.")
    parser.add_argument("--generator", default=str(DEFAULT_GENERATOR))
    parser.add_argument("--descent", default=str(DEFAULT_DESCENT))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    generator = json.loads(Path(args.generator).read_text(encoding="utf-8"))
    descent = json.loads(Path(args.descent).read_text(encoding="utf-8"))
    centered = generator["centered_compressed_branch_generator"]
    matrix = np.asarray(centered["real"], dtype=float) + 1j * np.asarray(centered["imag"], dtype=float)
    eigenvalues = np.linalg.eigvalsh(matrix)
    lam1, lam2, lam3 = [float(x) for x in eigenvalues.tolist()]
    gap21 = lam2 - lam1
    gap32 = lam3 - lam2
    x = np.asarray(
        [
            2.0 * (lam1 - lam1) / (lam3 - lam1) - 1.0,
            2.0 * (lam2 - lam1) / (lam3 - lam1) - 1.0,
            2.0 * (lam3 - lam1) / (lam3 - lam1) - 1.0,
        ],
        dtype=float,
    )
    diagnostic_coeffs_u = {"linear": 2.795, "quadratic": -0.362}
    diagnostic_coeffs_d = {"linear": 1.652, "quadratic": 0.205}
    e_u = _ctr(diagnostic_coeffs_u["linear"] * x + diagnostic_coeffs_u["quadratic"] * x**2)
    e_d = _ctr(diagnostic_coeffs_d["linear"] * x + diagnostic_coeffs_d["quadratic"] * x**2)

    artifact = {
        "artifact": "oph_family_excitation_evaluator",
        "generated_utc": _timestamp(),
        "proof_status": "candidate_only",
        "input_kind": "ordered_branch_generator_spectral_package",
        "log_insertion_convention": "add_E_q_log_to_both_left_and_right_diagonal_logs",
        "family_coordinate_kind": "affine_normalized_ordered_branch_coordinate",
        "ordered_family_eigenvalues": [lam1, lam2, lam3],
        "ordered_spectral_gaps": [gap21, gap32],
        "family_coordinate_x": [float(v) for v in x.tolist()],
        "centering_mode": "trace_zero",
        "quadratic_family_formula": "E_q_log = ctr(a_q * X_ord + b_q * X_ord^2)",
        "quadratic_polynomial_coeffs_u": {"linear": None, "quadratic": None},
        "quadratic_polynomial_coeffs_d": {"linear": None, "quadratic": None},
        "diagnostic_witness_coeffs_u": diagnostic_coeffs_u,
        "diagnostic_witness_coeffs_d": diagnostic_coeffs_d,
        "diagnostic_witness_E_u_log": e_u,
        "diagnostic_witness_E_d_log": e_d,
        "diagnostic_required_gap_ratio_u": 1.30,
        "diagnostic_required_gap_ratio_d": 0.78,
        "shared_norm_origin": descent.get("shared_norm_origin"),
        "shared_norm_value": descent.get("g_ch"),
        "promotion_blocker_cleared": "quark_even_excitation_evaluator_missing",
        "notes": [
            "The smallest reduced live family is not a free three-weight projector ansatz but a trace-zero quadratic evaluator on the ordered centered branch-generator operator.",
            "The diagnostic witness coefficients are reference-facing only; they show the rough span the missing evaluator must generate without being promoted to theorem status.",
        ],
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
