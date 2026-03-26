import json
import pathlib
import sys
import unittest

import yaml


ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class HadronDemoNotPromotedTest(unittest.TestCase):
    def test_hadron_ledger_tier_stays_simulation_dependent(self) -> None:
        ledger = yaml.safe_load((ROOT /  "ledger.yaml").read_text(encoding="utf-8"))
        entries = {entry["id"]: entry for entry in ledger["entries"]}
        self.assertEqual(entries["simulation.hadrons.current_lane"]["tier"], "simulation_dependent")

    def test_current_reference_artifact_classifies_as_smoke(self) -> None:
        from hadron.systematics_report import classify_reference_artifact

        payload = json.loads(
            (ROOT /  "runs" / "hadron" / "quenched-reference-20260324T131847Z.json").read_text(encoding="utf-8")
        )
        classification = classify_reference_artifact(payload)
        self.assertEqual(classification["lane_status"], "smoke")
        self.assertIn("quenched", classification["blockers"])


if __name__ == "__main__":
    unittest.main()
