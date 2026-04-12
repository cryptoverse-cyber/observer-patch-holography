#!/usr/bin/env python3
"""Emit the exact current-family light-ratio theorem.

Chain role: expose the exact light-quark mass-ratio scalar already determined
on the target-anchored current-family witness.

Mathematics: on the exact current-family readout witness,
m_u = g_u * exp(E_u_log_exact[0]) and m_d = g_d * exp(E_d_log_exact[0]),
so the light-ratio scalar is
ell_ud = log(m_d / m_u)
       = log(g_d / g_u) + E_d_log_exact[0] - E_u_log_exact[0].

Output: one theorem-shaped artifact on `current_family_only` that makes this
exact light-ratio scalar explicit without promoting it to the public
target-free theorem `H_mass`.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
EXACT_READOUT_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_exact_readout.json"
SELECTED_SHEET_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_selected_sheet_closure.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_light_ratio_theorem.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload(exact_readout: dict[str, Any], selected_sheet: dict[str, Any] | None = None) -> dict[str, Any]:
    m_u = float(exact_readout["predicted_singular_values_u"][0])
    m_d = float(exact_readout["predicted_singular_values_d"][0])
    g_u = float(exact_readout["g_u"])
    g_d = float(exact_readout["g_d"])
    e_u_1 = float(exact_readout["E_u_log_exact"][0])
    e_d_1 = float(exact_readout["E_d_log_exact"][0])
    ell_ud = math.log(m_d / m_u)
    decomposition = math.log(g_d / g_u) + e_d_1 - e_u_1
    payload = {
        "artifact": "oph_quark_current_family_light_ratio_theorem",
        "generated_utc": _timestamp(),
        "proof_status": "closed_current_family_light_ratio_theorem",
        "theorem_scope": "current_family_only",
        "public_promotion_allowed": False,
        "theorem_statement": (
            "On the exact current-family quark witness, the light mass-ratio scalar is exact: "
            "ell_ud := log(m_d / m_u) = log(g_d / g_u) + E_d_log_exact[1st] - E_u_log_exact[1st]. "
            "Equivalently, the target-anchored current-family witness determines a unique exact "
            "light-quark ratio m_d / m_u."
        ),
        "supporting_artifacts": {
            "exact_readout": exact_readout["artifact"],
            "selected_sheet_closure": None if selected_sheet is None else selected_sheet["artifact"],
        },
        "selected_sheet": None if selected_sheet is None else selected_sheet["selected_sheet"],
        "exact_light_data": {
            "m_u": m_u,
            "m_d": m_d,
            "m_d_over_m_u": m_d / m_u,
            "m_u_over_m_d": m_u / m_d,
            "ell_ud": ell_ud,
        },
        "exact_readout_decomposition": {
            "m_u_formula": "g_u * exp(E_u_log_exact[0])",
            "m_d_formula": "g_d * exp(E_d_log_exact[0])",
            "ell_ud_formula": "log(g_d / g_u) + E_d_log_exact[0] - E_u_log_exact[0]",
            "log_g_ratio": math.log(g_d / g_u),
            "E_u_log_exact_0": e_u_1,
            "E_d_log_exact_0": e_d_1,
            "ell_ud_from_decomposition": decomposition,
            "decomposition_residual": decomposition - ell_ud,
        },
        "theorem_boundary_note": (
            "This is an exact theorem on the target-anchored current-family witness. "
            "It does not by itself emit the public target-free object H_mass := log(c_d / c_u)."
        ),
        "next_bridge_to_public_frontier": {
            "public_missing_object": "light_quark_overlap_defect_value_law",
            "public_missing_formula": "Delta_ud_overlap = (1/6) * log(c_d / c_u)",
            "why_not_done": (
                "The present theorem uses the exact current-family witness and therefore fixes "
                "log(m_d / m_u), not the target-free coefficient ratio log(c_d / c_u)."
            ),
        },
        "target_anchored_d12_route_if_adjoined": {
            "Delta_ud_overlap_formula": "(1/6) * ell_ud",
            "t1_formula": "(5/6) * ell_ud",
        },
        "notes": [
            "This theorem is deliberately narrower than H_mass.",
            "It provides an exact current-family light-ratio scalar that can be compared against any proposed public D12 value law.",
        ],
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the exact current-family light-ratio theorem artifact.")
    parser.add_argument("--exact-readout", default=str(EXACT_READOUT_JSON))
    parser.add_argument("--selected-sheet", default=str(SELECTED_SHEET_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    selected_path = Path(args.selected_sheet)
    payload = build_payload(
        _load_json(Path(args.exact_readout)),
        _load_json(selected_path) if selected_path.exists() else None,
    )
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
