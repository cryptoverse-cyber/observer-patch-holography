#!/usr/bin/env python3
"""Guard the realized transported cap-local UV system artifact."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "uv" / "derive_bw_realized_transported_cap_local_system.py"
OUTPUT = ROOT / "particles" / "runs" / "uv" / "bw_realized_transported_cap_local_system.json"


def test_bw_realized_transported_cap_local_system() -> None:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--output", str(OUTPUT)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "saved:" in completed.stdout
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert payload["artifact"] == "oph_realized_transported_cap_local_system"
    assert payload["status"] == "constructed_prelimit_system_two_lower_emitted_witnesses_still_missing"
    assert payload["fills_contract_witnesses"] == [
        "reference_cap_local_test_system",
        "projectively_compatible_transported_cap_marginal_family",
        "asymptotic_transport_equivalence_certificate",
    ]
    assert payload["remaining_missing_emitted_witness"] == "vanishing_carried_collar_schedule_on_fixed_local_collars"
    assert payload["remaining_missing_witness_contract"]["artifact"].endswith("bw_carried_collar_schedule_scaffold.json")
    assert payload["remaining_missing_witness_contract"]["formula"].startswith("eta_{n,m,delta} = r_FR")
    assert payload["smaller_remaining_raw_datum"]["id"] == "fixed_local_collar_markov_faithfulness_datum"
    assert payload["smaller_remaining_raw_datum"]["artifact"].endswith("bw_fixed_local_collar_markov_faithfulness_datum.json")
    witness_chain = payload["remaining_witness_decomposition"]
    assert [entry["id"] for entry in witness_chain] == [
        "constructive_recovery_remainder_vanishing",
        "fixed_local_collar_exact_markov_modulus_vanishing",
        "fixed_local_collar_faithful_modular_defect_vanishing",
        "vanishing_carried_collar_schedule_on_fixed_local_collars",
    ]
    assert [entry["id"] for entry in payload["schedule_term_witnesses"]] == [
        "constructive_recovery_remainder_vanishing",
        "fixed_local_collar_faithful_modular_defect_vanishing",
    ]
    assert [entry["id"] for entry in payload["actual_solver_missing_emitted_witnesses"]] == [
        "constructive_recovery_remainder_vanishing",
        "fixed_local_collar_faithful_modular_defect_vanishing",
    ]
    assert payload["derived_remaining_input_witness"]["id"] == "vanishing_carried_collar_schedule_on_fixed_local_collars"
    ledger = payload["remaining_witness_obligation_ledger"]
    assert ledger[0]["id"] == "collarwise_markov_input"
    assert ledger[-1]["artifact"].endswith("bw_carried_collar_schedule_scaffold.json")
    gate = payload["remaining_witness_support_gate"]
    assert gate["status"] == "open"
    assert len(gate["insufficient_on_their_own"]) == 4
    assert gate["insufficient_on_their_own"][0]["artifact"].endswith(
        "bw_fixed_local_collar_constructive_recovery_scaffold.json"
    )
    assert payload["next_exact_object"]["id"] == "canonical_scaling_cap_pair_realization_from_transported_cap_marginals"
