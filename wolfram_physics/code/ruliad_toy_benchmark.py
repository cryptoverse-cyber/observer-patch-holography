#!/usr/bin/env python3
"""Reconstruct the toy benchmark from the OPH/ruliad bridge paper.

This script computes the reported toy-harness counts from first principles.
It does not use the published totals to drive the computation. The expected
paper values are only used at the end as an optional consistency check.

Operational assumptions
-----------------------
The current TeX paper states the toy corpus, packet bits, and reported counts,
but omits a few implementation details needed to reproduce them mechanically.
Those details are taken from the audited bridge notes that accompanied the
paper draft:

1. Histories are all rooted paths from E of lengths 0..L, not only maximal
   paths.
2. Repair sends a packet to the nearest consistent packet in Hamming distance
   on the four bits (ell, chi, t, tau), with ties broken by preserving the
   observed branch bit ell.
3. The confluence filter keeps rule families for which all reachable histories
   repair to the same packet normal form.
4. The holonomy filter keeps rule families for which every reachable history
   has vanishing cycle sum.
5. The toy finite-constraint stage records kappa_toy = |Supp_pkt|-1, but the
   paper does not specify an exclusion threshold beyond the first two filters,
   so that stage is reporting-only in this harness.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import asdict, dataclass
from itertools import combinations
from pathlib import Path
from typing import DefaultDict, Iterable

Edge = tuple[str, str]
History = tuple[str, ...]
Packet = tuple[int, int, int, int]

EDGE_ORDER: tuple[Edge, ...] = (
    ("E", "F"),
    ("E", "H"),
    ("F", "G"),
    ("H", "G"),
    ("F", "F"),
    ("H", "H"),
    ("F", "H"),
    ("H", "F"),
)
EDGE_INDEX = {edge: index for index, edge in enumerate(EDGE_ORDER)}

INITIAL_STATE = "E"
MAX_DEPTH = 3
RULE_FAMILY_SIZES = (2, 3, 4)

# The two defect-free packet states described in the bridge notes.
CONSISTENT_PACKETS: tuple[Packet, ...] = (
    (0, 0, 0, 0),
    (1, 0, 1, 1),
)

# Used only for post-computation verification.
PAPER_COUNTS = {
    "raw_rule_families": 154,
    "semantic_classes": 8,
    "largest_semantic_class": 71,
    "after_confluence": 103,
    "after_holonomy": 92,
    "after_toy_finite_constraint": 92,
    "surviving_semantic_classes": 2,
}


@dataclass(frozen=True)
class FamilyAnalysis:
    """Computed observer-visible data for a single toy rule family."""

    rule_family: tuple[Edge, ...]
    history_count: int
    packet_support: tuple[Packet, ...]
    normal_form_support: tuple[Packet, ...]
    support_rank: int
    confluence_pass: bool
    holonomy_pass: bool
    survives_early_search: bool

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["rule_family"] = [edge_to_str(edge) for edge in self.rule_family]
        data["packet_support"] = [list(packet) for packet in self.packet_support]
        data["normal_form_support"] = [
            list(packet) for packet in self.normal_form_support
        ]
        return data


@dataclass(frozen=True)
class SemanticClass:
    """Observer-visible semantic quotient class."""

    class_id: int
    packet_support: tuple[Packet, ...]
    normal_form_support: tuple[Packet, ...]
    family_count: int
    representative_family: tuple[Edge, ...]
    survives_early_search: bool

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["packet_support"] = [list(packet) for packet in self.packet_support]
        data["normal_form_support"] = [
            list(packet) for packet in self.normal_form_support
        ]
        data["representative_family"] = [
            edge_to_str(edge) for edge in self.representative_family
        ]
        return data


def edge_to_str(edge: Edge) -> str:
    return f"{edge[0]}->{edge[1]}"


def canonical_rule_family(edges: Iterable[Edge]) -> tuple[Edge, ...]:
    """Sort a rule family in the canonical order used in the paper."""
    return tuple(sorted(edges, key=EDGE_INDEX.__getitem__))


def enumerate_rule_families() -> tuple[tuple[Edge, ...], ...]:
    """Enumerate all size-2/3/4 families from the eight toy edges."""
    families: list[tuple[Edge, ...]] = []
    for size in RULE_FAMILY_SIZES:
        for rule_family in combinations(EDGE_ORDER, size):
            families.append(canonical_rule_family(rule_family))
    return tuple(families)


def enumerate_histories(rule_family: tuple[Edge, ...]) -> tuple[History, ...]:
    """Enumerate all rooted histories from E of lengths 0..MAX_DEPTH.

    The benchmark counts depend on including every prefix history, not only
    maximal histories. That convention is explicit here to avoid accidental
    drift in later rewrites.
    """

    outgoing: DefaultDict[str, list[str]] = defaultdict(list)
    for src, dst in rule_family:
        outgoing[src].append(dst)

    histories: list[History] = []

    def walk(history: History) -> None:
        histories.append(history)
        depth = len(history) - 1
        if depth == MAX_DEPTH:
            return

        current = history[-1]
        for dst in outgoing.get(current, []):
            walk(history + (dst,))

    walk((INITIAL_STATE,))
    return tuple(histories)


def packet_from_history(rule_family: tuple[Edge, ...], history: History) -> Packet:
    """Compute the toy observer packet for one history."""
    rule_family_set = frozenset(rule_family)

    ell = int(len(history) >= 2 and history[1] == "H")
    chi = int(("E", "F") in rule_family_set and ("E", "H") in rule_family_set)
    t = int("G" in history)
    tau = t
    return (ell, chi, t, tau)


def overlap_defects(packet: Packet) -> tuple[int, int, int]:
    """Return the three Z_2 overlap defects (before mod-2 reduction)."""
    ell, chi, t, tau = packet
    b12 = ell - t
    b23 = t - tau
    b31 = tau - (ell ^ chi)
    return (b12, b23, b31)


def cycle_sum(packet: Packet) -> int:
    """Compute the oriented cycle sum modulo 2."""
    return sum(overlap_defects(packet)) % 2


def hamming_distance(left: Packet, right: Packet) -> int:
    return sum(a != b for a, b in zip(left, right))


def repair_packet(packet: Packet) -> Packet:
    """Repair a packet to the nearest consistent state.

    If both consistent packets are equally close, preserve the observed branch
    bit ell when breaking the tie.
    """

    distances = [
        (hamming_distance(packet, candidate), candidate)
        for candidate in CONSISTENT_PACKETS
    ]
    best_distance = min(distance for distance, _ in distances)
    tied_candidates = [
        candidate for distance, candidate in distances if distance == best_distance
    ]
    if len(tied_candidates) == 1:
        return tied_candidates[0]

    observed_ell = packet[0]
    for candidate in tied_candidates:
        if candidate[0] == observed_ell:
            return candidate
    return tied_candidates[0]


def analyze_rule_family(rule_family: tuple[Edge, ...]) -> FamilyAnalysis:
    histories = enumerate_histories(rule_family)
    packets = tuple(packet_from_history(rule_family, history) for history in histories)
    repaired_packets = tuple(repair_packet(packet) for packet in packets)

    packet_support = tuple(sorted(set(packets)))
    normal_form_support = tuple(sorted(set(repaired_packets)))

    confluence_pass = len(normal_form_support) == 1
    holonomy_pass = all(cycle_sum(packet) == 0 for packet in packets)
    survives_early_search = confluence_pass and holonomy_pass

    return FamilyAnalysis(
        rule_family=rule_family,
        history_count=len(histories),
        packet_support=packet_support,
        normal_form_support=normal_form_support,
        support_rank=len(packet_support) - 1,
        confluence_pass=confluence_pass,
        holonomy_pass=holonomy_pass,
        survives_early_search=survives_early_search,
    )


def build_semantic_classes(
    analyses: tuple[FamilyAnalysis, ...],
) -> tuple[SemanticClass, ...]:
    grouped: DefaultDict[
        tuple[tuple[Packet, ...], tuple[Packet, ...]], list[FamilyAnalysis]
    ] = defaultdict(list)

    for analysis in analyses:
        signature = (analysis.packet_support, analysis.normal_form_support)
        grouped[signature].append(analysis)

    ordered_groups = sorted(
        grouped.items(),
        key=lambda item: (-len(item[1]), item[0][0], item[0][1]),
    )

    semantic_classes: list[SemanticClass] = []
    for class_id, ((packet_support, normal_form_support), members) in enumerate(
        ordered_groups, start=1
    ):
        representative = min(members, key=lambda analysis: analysis.rule_family)
        semantic_classes.append(
            SemanticClass(
                class_id=class_id,
                packet_support=packet_support,
                normal_form_support=normal_form_support,
                family_count=len(members),
                representative_family=representative.rule_family,
                survives_early_search=any(
                    member.survives_early_search for member in members
                ),
            )
        )

    return tuple(semantic_classes)


def build_summary(
    analyses: tuple[FamilyAnalysis, ...], semantic_classes: tuple[SemanticClass, ...]
) -> dict[str, object]:
    raw_rule_families = len(analyses)
    after_confluence = sum(analysis.confluence_pass for analysis in analyses)
    after_holonomy = sum(
        analysis.confluence_pass and analysis.holonomy_pass for analysis in analyses
    )

    # The current toy paper records kappa_toy but does not add a separate cutoff.
    after_toy_finite_constraint = after_holonomy

    largest_semantic_class = max(
        semantic_class.family_count for semantic_class in semantic_classes
    )
    surviving_semantic_classes = sum(
        semantic_class.survives_early_search for semantic_class in semantic_classes
    )

    return {
        "raw_rule_families": raw_rule_families,
        "semantic_classes": len(semantic_classes),
        "largest_semantic_class": largest_semantic_class,
        "after_confluence": after_confluence,
        "after_holonomy": after_holonomy,
        "after_toy_finite_constraint": after_toy_finite_constraint,
        "rejected_total": raw_rule_families - after_toy_finite_constraint,
        "rejection_rate": (
            (raw_rule_families - after_toy_finite_constraint) / raw_rule_families
        ),
        "surviving_semantic_classes": surviving_semantic_classes,
    }


def benchmark_payload() -> dict[str, object]:
    analyses = tuple(analyze_rule_family(rule_family) for rule_family in enumerate_rule_families())
    semantic_classes = build_semantic_classes(analyses)
    summary = build_summary(analyses, semantic_classes)

    return {
        "assumptions": {
            "history_convention": "all rooted paths from E of lengths 0..3",
            "repair_rule": (
                "nearest consistent packet in Hamming distance with ell-preserving tie-break"
            ),
            "confluence_filter": (
                "all reachable histories repair to the same packet normal form"
            ),
            "holonomy_filter": "every reachable history has vanishing cycle sum",
            "toy_finite_constraint_stage": (
                "records kappa_toy = |Supp_pkt|-1 with no extra exclusion threshold"
            ),
        },
        "summary": summary,
        "semantic_classes": [semantic_class.to_dict() for semantic_class in semantic_classes],
        "rule_families": [analysis.to_dict() for analysis in analyses],
    }


def verify_paper_counts(summary: dict[str, object]) -> None:
    mismatches = []
    for key, expected in PAPER_COUNTS.items():
        actual = summary[key]
        if actual != expected:
            mismatches.append((key, expected, actual))

    if mismatches:
        lines = ["Computed counts do not match the paper values:"]
        for key, expected, actual in mismatches:
            lines.append(f"  {key}: expected {expected}, got {actual}")
        raise SystemExit("\n".join(lines))


def print_report(payload: dict[str, object]) -> None:
    summary = payload["summary"]

    print("Toy benchmark summary")
    print(f"  raw rule families: {summary['raw_rule_families']}")
    print(f"  semantic classes: {summary['semantic_classes']}")
    print(f"  largest semantic class: {summary['largest_semantic_class']}")
    print(f"  after confluence: {summary['after_confluence']}")
    print(f"  after holonomy: {summary['after_holonomy']}")
    print(
        "  after toy finite-constraint stage: "
        f"{summary['after_toy_finite_constraint']}"
    )
    print(f"  total rejected: {summary['rejected_total']}")
    print(f"  rejection rate: {summary['rejection_rate']:.6f}")
    print(
        "  surviving semantic classes: "
        f"{summary['surviving_semantic_classes']}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reconstruct the OPH/ruliad toy benchmark."
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        help="Optional path for a JSON dump of all computed benchmark data.",
    )
    parser.add_argument(
        "--skip-paper-check",
        action="store_true",
        help="Skip verification against the counts reported in the paper.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = benchmark_payload()

    if not args.skip_paper_check:
        verify_paper_counts(payload["summary"])

    print_report(payload)

    if args.json_out is not None:
        args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True))
        print(f"Wrote JSON report to {args.json_out}")


if __name__ == "__main__":
    main()
