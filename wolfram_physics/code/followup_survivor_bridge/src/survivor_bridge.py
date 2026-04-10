#!/usr/bin/env python3
"""Finite-survivor-quotient bridge machinery for the follow-up draft.

This module does not recompute the original raw rule-family benchmark. Instead,
it starts from the computed 8-class semantic quotient from
`ruliad_toy_benchmark_results.json` and builds a theorem-witness layer on top.

The toy witness layer has three purposes:

1. define a concrete defect vector on the 8 semantic classes;
2. define a deterministic nearest-improvement update that strictly decreases
   the defect vector off the minimal sector;
3. define a primitive noisy kernel on the 2-class minimal sector and compute
   its unique stationary law.

The deterministic witness operator is intentionally presented as a theorem
widget, not as a claimed canonical microphysical refinement law.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

Packet = tuple[int, int, int, int]
Defect = tuple[int, int]

DEFAULT_BENCHMARK_RESULTS = (
    Path(__file__).resolve().parents[2] / "ruliad_toy_benchmark_results.json"
)


@dataclass(frozen=True)
class ToySemanticClass:
    """One semantic quotient class from the earlier toy benchmark."""

    class_id: int
    packet_support: tuple[Packet, ...]
    normal_form_support: tuple[Packet, ...]
    family_count: int
    representative_family: tuple[str, ...]
    survives_early_search: bool


def cycle_sum(packet: Packet) -> int:
    ell, chi, t, tau = packet
    return (ell - t + t - tau + tau - (ell ^ chi)) % 2


def hamming_distance(left: Packet, right: Packet) -> int:
    return sum(a != b for a, b in zip(left, right))


def load_toy_semantic_classes(
    results_path: Path = DEFAULT_BENCHMARK_RESULTS,
) -> tuple[ToySemanticClass, ...]:
    payload = json.loads(results_path.read_text())
    classes = []
    for raw_class in payload["semantic_classes"]:
        classes.append(
            ToySemanticClass(
                class_id=raw_class["class_id"],
                packet_support=tuple(tuple(packet) for packet in raw_class["packet_support"]),
                normal_form_support=tuple(
                    tuple(packet) for packet in raw_class["normal_form_support"]
                ),
                family_count=raw_class["family_count"],
                representative_family=tuple(raw_class["representative_family"]),
                survives_early_search=raw_class["survives_early_search"],
            )
        )
    return tuple(classes)


def defect_vector(semantic_class: ToySemanticClass) -> Defect:
    """Return the 2-component defect vector used in the follow-up draft.

    Component 1:
      ambiguity defect = number of distinct normal forms minus one

    Component 2:
      holonomy defect = max cycle-sum flag over the packet support
    """

    ambiguity = len(semantic_class.normal_form_support) - 1
    holonomy = max(cycle_sum(packet) for packet in semantic_class.packet_support)
    return (ambiguity, holonomy)


def support_distance(
    source: ToySemanticClass, target: ToySemanticClass
) -> int:
    """Distance from one packet support to another.

    This is used to define a transparent nearest-improvement witness dynamics on
    the semantic quotient.
    """

    total = 0
    for packet in source.packet_support:
        total += min(
            hamming_distance(packet, candidate) for candidate in target.packet_support
        )
    return total


def class_index(
    classes: Iterable[ToySemanticClass],
) -> dict[int, ToySemanticClass]:
    return {semantic_class.class_id: semantic_class for semantic_class in classes}


def minimal_sector(
    classes: tuple[ToySemanticClass, ...],
) -> tuple[ToySemanticClass, ...]:
    defects = {semantic_class.class_id: defect_vector(semantic_class) for semantic_class in classes}
    min_defect = min(defects.values())
    return tuple(
        semantic_class
        for semantic_class in classes
        if defects[semantic_class.class_id] == min_defect
    )


def build_nearest_improvement_update(
    classes: tuple[ToySemanticClass, ...],
) -> dict[int, int]:
    """Build a deterministic witness update on the finite quotient.

    Every nonminimal class moves to the lower-defect class with smallest packet
    support distance. Minimal classes are fixed.
    """

    defects = {semantic_class.class_id: defect_vector(semantic_class) for semantic_class in classes}
    update: dict[int, int] = {}

    for semantic_class in classes:
        current_defect = defects[semantic_class.class_id]
        lower_candidates = [
            candidate
            for candidate in classes
            if defects[candidate.class_id] < current_defect
        ]
        if not lower_candidates:
            update[semantic_class.class_id] = semantic_class.class_id
            continue

        target = min(
            lower_candidates,
            key=lambda candidate: (
                support_distance(semantic_class, candidate),
                candidate.class_id,
            ),
        )
        update[semantic_class.class_id] = target.class_id

    return update


def orbit(update: dict[int, int], start: int) -> tuple[int, ...]:
    path = [start]
    seen = {start}
    while True:
        nxt = update[path[-1]]
        path.append(nxt)
        if nxt == path[-2]:
            return tuple(path)
        if nxt in seen:
            raise ValueError(f"Cycle detected in witness dynamics from state {start}")
        seen.add(nxt)


def update_steps_to_fixpoint(update: dict[int, int], start: int) -> int:
    return len(orbit(update, start)) - 2


def verify_strict_lexicographic_descent(
    classes: tuple[ToySemanticClass, ...],
    update: dict[int, int],
) -> bool:
    by_id = class_index(classes)
    for state, target in update.items():
        if state == target:
            continue
        if not defect_vector(by_id[target]) < defect_vector(by_id[state]):
            return False
    return True


def build_minimal_sector_kernel(
    survivor_classes: tuple[ToySemanticClass, ...],
) -> dict[int, dict[int, float]]:
    """Build a primitive noisy kernel on the minimal 2-class sector."""

    if len(survivor_classes) != 2:
        raise ValueError("The toy witness kernel is defined only for 2 survivor classes")

    first, second = sorted((semantic_class.class_id for semantic_class in survivor_classes))
    return {
        first: {first: 0.8, second: 0.2},
        second: {first: 0.3, second: 0.7},
    }


def kernel_states(kernel: dict[int, dict[int, float]]) -> tuple[int, ...]:
    return tuple(sorted(kernel))


def is_stochastic_kernel(kernel: dict[int, dict[int, float]], tol: float = 1e-12) -> bool:
    states = kernel_states(kernel)
    for state in states:
        row = kernel[state]
        if set(row) != set(states):
            return False
        if any(value < 0 for value in row.values()):
            return False
        if abs(sum(row.values()) - 1.0) > tol:
            return False
    return True


def kernel_matrix(kernel: dict[int, dict[int, float]]) -> tuple[tuple[float, ...], ...]:
    states = kernel_states(kernel)
    return tuple(tuple(kernel[state][target] for target in states) for state in states)


def matrix_multiply(
    left: tuple[tuple[float, ...], ...],
    right: tuple[tuple[float, ...], ...],
) -> tuple[tuple[float, ...], ...]:
    size = len(left)
    return tuple(
        tuple(sum(left[i][k] * right[k][j] for k in range(size)) for j in range(size))
        for i in range(size)
    )


def is_primitive(kernel: dict[int, dict[int, float]]) -> bool:
    matrix = kernel_matrix(kernel)
    size = len(matrix)
    power = matrix
    for _ in range(1, size * size + 1):
        if all(entry > 0 for row in power for entry in row):
            return True
        power = matrix_multiply(power, matrix)
    return False


def push_forward_distribution(
    distribution: tuple[float, ...],
    kernel: dict[int, dict[int, float]],
) -> tuple[float, ...]:
    states = kernel_states(kernel)
    return tuple(
        sum(distribution[i] * kernel[states[i]][states[j]] for i in range(len(states)))
        for j in range(len(states))
    )


def stationary_distribution(
    kernel: dict[int, dict[int, float]],
    iterations: int = 256,
) -> dict[int, float]:
    if not is_stochastic_kernel(kernel):
        raise ValueError("Kernel is not row-stochastic")

    states = kernel_states(kernel)
    distribution = tuple(1.0 / len(states) for _ in states)
    for _ in range(iterations):
        distribution = push_forward_distribution(distribution, kernel)
    return {state: weight for state, weight in zip(states, distribution)}


def build_report(
    results_path: Path = DEFAULT_BENCHMARK_RESULTS,
) -> dict[str, object]:
    classes = load_toy_semantic_classes(results_path)
    defects = {
        semantic_class.class_id: list(defect_vector(semantic_class))
        for semantic_class in classes
    }
    update = build_nearest_improvement_update(classes)
    survivor_classes = minimal_sector(classes)
    kernel = build_minimal_sector_kernel(survivor_classes)
    stationary = stationary_distribution(kernel)

    return {
        "input_results": str(results_path),
        "semantic_class_count": len(classes),
        "minimal_sector": [semantic_class.class_id for semantic_class in survivor_classes],
        "defect_vectors": defects,
        "nearest_improvement_update": update,
        "strict_lexicographic_descent": verify_strict_lexicographic_descent(
            classes, update
        ),
        "orbits": {
            semantic_class.class_id: list(orbit(update, semantic_class.class_id))
            for semantic_class in classes
        },
        "max_steps_to_fixpoint": max(
            update_steps_to_fixpoint(update, semantic_class.class_id)
            for semantic_class in classes
        ),
        "minimal_sector_kernel": {
            state: kernel[state] for state in kernel_states(kernel)
        },
        "kernel_is_primitive": is_primitive(kernel),
        "stationary_distribution": stationary,
    }


def print_report(report: dict[str, object]) -> None:
    print("Follow-up survivor bridge summary")
    print(f"  semantic classes: {report['semantic_class_count']}")
    print(f"  minimal sector: {report['minimal_sector']}")
    print(f"  strict lexicographic descent: {report['strict_lexicographic_descent']}")
    print(f"  max steps to fixpoint: {report['max_steps_to_fixpoint']}")
    print(f"  primitive kernel on minimal sector: {report['kernel_is_primitive']}")
    print(f"  stationary distribution: {report['stationary_distribution']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the toy survivor-bridge witness system."
    )
    parser.add_argument(
        "--results-path",
        type=Path,
        default=DEFAULT_BENCHMARK_RESULTS,
        help="Path to ruliad_toy_benchmark_results.json",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        help="Optional path for a JSON dump of the survivor-bridge report.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = build_report(args.results_path)
    print_report(report)
    if args.json_out is not None:
        args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True))
        print(f"Wrote JSON report to {args.json_out}")


if __name__ == "__main__":
    main()
