#!/usr/bin/env python3
"""Regression checks for the follow-up survivor-bridge witness package."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[1] / "src"
    ),
)

import survivor_bridge


class SurvivorBridgeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.classes = survivor_bridge.load_toy_semantic_classes()
        self.update = survivor_bridge.build_nearest_improvement_update(self.classes)
        self.minimal_sector = survivor_bridge.minimal_sector(self.classes)
        self.kernel = survivor_bridge.build_minimal_sector_kernel(self.minimal_sector)

    def test_semantic_quotient_has_eight_classes(self) -> None:
        self.assertEqual(len(self.classes), 8)

    def test_defect_minimal_sector_has_two_classes(self) -> None:
        self.assertEqual(
            tuple(semantic_class.class_id for semantic_class in self.minimal_sector),
            (1, 2),
        )

    def test_nearest_improvement_update_matches_expected_witness(self) -> None:
        self.assertEqual(
            self.update,
            {1: 1, 2: 2, 3: 1, 4: 2, 5: 2, 6: 5, 7: 5, 8: 5},
        )

    def test_update_strictly_decreases_defect_off_fixpoints(self) -> None:
        self.assertTrue(
            survivor_bridge.verify_strict_lexicographic_descent(
                self.classes, self.update
            )
        )

    def test_all_orbits_reach_fixpoints_within_two_updates(self) -> None:
        steps = [
            survivor_bridge.update_steps_to_fixpoint(self.update, semantic_class.class_id)
            for semantic_class in self.classes
        ]
        self.assertLessEqual(max(steps), 2)

    def test_minimal_sector_kernel_is_primitive(self) -> None:
        self.assertTrue(survivor_bridge.is_primitive(self.kernel))

    def test_stationary_distribution_is_the_expected_two_class_law(self) -> None:
        stationary = survivor_bridge.stationary_distribution(self.kernel)
        self.assertAlmostEqual(stationary[1], 0.6, places=8)
        self.assertAlmostEqual(stationary[2], 0.4, places=8)


if __name__ == "__main__":
    unittest.main()
