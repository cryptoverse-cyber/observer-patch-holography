#!/usr/bin/env python3
"""Regression checks for the toy benchmark reconstruction."""

from __future__ import annotations

import unittest

import ruliad_toy_benchmark as benchmark


class ToyBenchmarkTests(unittest.TestCase):
    def test_paper_counts_match(self) -> None:
        payload = benchmark.benchmark_payload()
        benchmark.verify_paper_counts(payload["summary"])

    def test_consistent_packets_are_exactly_the_two_bridge_states(self) -> None:
        self.assertEqual(
            benchmark.CONSISTENT_PACKETS,
            ((0, 0, 0, 0), (1, 0, 1, 1)),
        )

    def test_holonomy_identity_matches_branching_bit(self) -> None:
        payload = benchmark.benchmark_payload()
        for family in payload["rule_families"]:
            for packet in family["packet_support"]:
                ell, chi, t, tau = packet
                cycle = benchmark.cycle_sum((ell, chi, t, tau))
                self.assertEqual(cycle, chi % 2)

    def test_two_semantic_classes_survive_early_search(self) -> None:
        payload = benchmark.benchmark_payload()
        survivors = [
            semantic_class
            for semantic_class in payload["semantic_classes"]
            if semantic_class["survives_early_search"]
        ]
        self.assertEqual(len(survivors), 2)


if __name__ == "__main__":
    unittest.main()
