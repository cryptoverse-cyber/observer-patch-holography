#!/usr/bin/env python3
"""Build blind charged-lepton shape and absolute-scale artifacts."""

from __future__ import annotations

import argparse
import json
import pathlib
from datetime import datetime, timezone
from typing import Any

import numpy as np


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT /  "runs" / "leptons" / "lepton_descent_tensor.json"
DEFAULT_CHANNEL_NORM = ROOT /  "runs" / "leptons" / "lepton_channel_norm.json"
DEFAULT_OUT = ROOT /  "runs" / "leptons" / "forward_charged_leptons.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _encode_complex_matrix(matrix: np.ndarray) -> dict[str, Any]:
    return {
        "real": np.real(matrix).tolist(),
        "imag": np.imag(matrix).tolist(),
    }


def _decode_complex_matrix(name: str, payload: Any) -> np.ndarray:
    if isinstance(payload, dict) and "real" in payload and "imag" in payload:
        matrix = np.asarray(payload["real"], dtype=float) + 1j * np.asarray(payload["imag"], dtype=float)
    else:
        matrix = np.asarray(payload, dtype=complex)
    if matrix.shape != (3, 3):
        raise ValueError(f"{name} must be a 3x3 matrix")
    return matrix


def _svd_data(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    u_left, singular_values, v_right_h = np.linalg.svd(matrix)
    order = np.argsort(singular_values)
    singular_values = singular_values[order]
    u_left = u_left[:, order]
    v_right = v_right_h.conj().T[:, order]
    return singular_values, u_left, v_right


def build_artifact(payload: dict[str, Any], channel_norm_payload: dict[str, Any] | None) -> dict[str, Any]:
    if "Y_e_shape" in payload:
        y_e_shape = _decode_complex_matrix("Y_e_shape", payload["Y_e_shape"])
        source_mode = "explicit_shape_matrix"
    elif "C_e_hat" in payload:
        c_e_hat = dict(payload.get("C_e_hat", {}))
        y_e_shape = _decode_complex_matrix("C_e_hat_matrix", c_e_hat.get("C_e_hat_matrix"))
        source_mode = "channel_tensor_shape"
    elif "Y_e" in payload:
        y_e_shape = _decode_complex_matrix("Y_e", payload["Y_e"])
        source_mode = "explicit_matrix"
    else:
        raise ValueError("Input must provide C_e_hat or Y_e_shape")

    singular_values_shape, u_e_left, u_e_right = _svd_data(y_e_shape)
    shape_closed = bool(payload.get("shape_closed", False))
    channel_norm_payload = channel_norm_payload or {}
    channel_norm_closed = bool(channel_norm_payload.get("channel_norm_closed", False))
    proof_status = str(channel_norm_payload.get("proof_status", "open"))
    closure_route = channel_norm_payload.get("closure_route")
    g_e = channel_norm_payload.get("g_e")
    y_e = None
    singular_values_abs = None
    if channel_norm_closed and g_e is not None:
        g_e_float = float(g_e)
        y_e = g_e_float * y_e_shape
        singular_values_abs = [g_e_float * float(item) for item in singular_values_shape.tolist()]

    if shape_closed and channel_norm_closed and y_e is not None:
        closure_state = "absolute_scale_closed"
    elif shape_closed and proof_status == "shared_budget_only":
        closure_state = "shared_budget_only"
    elif shape_closed:
        closure_state = "ratio_closed"
    else:
        closure_state = "open"

    return {
        "artifact": "oph_forward_charged_leptons",
        "generated_utc": _timestamp(),
        "source_mode": source_mode,
        "labels": payload.get("labels"),
        "Y_e_shape": _encode_complex_matrix(y_e_shape),
        "singular_values_shape": [float(x) for x in singular_values_shape.tolist()],
        "Y_e": None if y_e is None else _encode_complex_matrix(y_e),
        "singular_values_abs": singular_values_abs,
        "U_e_left": _encode_complex_matrix(u_e_left),
        "U_e_right": _encode_complex_matrix(u_e_right),
        "shape_closed": shape_closed,
        "channel_norm": {
            "channel_norm_closed": channel_norm_closed,
            "g_e_candidate": channel_norm_payload.get("g_e_candidate"),
            "g_e": g_e,
            "g_e_by_refinement": channel_norm_payload.get("g_e_by_refinement"),
            "proof_status": proof_status,
            "closure_route": closure_route,
            "scale_scope": channel_norm_payload.get("scale_scope"),
            "shared_budget_key": channel_norm_payload.get("shared_budget_key"),
            "shared_budget_share_e": channel_norm_payload.get("shared_budget_share_e"),
            "beta_e_by_refinement": channel_norm_payload.get("beta_e_by_refinement"),
            "charged_budget_total_by_refinement": channel_norm_payload.get("charged_budget_total_by_refinement"),
        },
        "basis_contract": {
            "labels": payload.get("labels"),
            "orientation_preserved": bool(payload.get("projector_basis_provenance", {}).get("orientation_preserved", False)),
        },
        "closure_state": closure_state,
        "theorem_status": closure_state,
        "absolute_scale_closed": closure_state == "absolute_scale_closed",
        "metadata": {
            **dict(payload.get("metadata", {})),
            "channel_norm_artifact": channel_norm_payload.get("artifact"),
            "closure_route": closure_route,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build blind charged-lepton shape and absolute artifacts.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Input JSON path.")
    parser.add_argument(
        "--channel-norm",
        default=str(DEFAULT_CHANNEL_NORM),
        help="Optional channel-norm JSON path.",
    )
    parser.add_argument("--output", default=str(DEFAULT_OUT), help="Output JSON path.")
    args = parser.parse_args()

    payload = json.loads(pathlib.Path(args.input).read_text(encoding="utf-8"))
    channel_norm_path = pathlib.Path(args.channel_norm)
    channel_norm_payload = json.loads(channel_norm_path.read_text(encoding="utf-8")) if channel_norm_path.exists() else None
    artifact = build_artifact(payload, channel_norm_payload)

    out_path = pathlib.Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
