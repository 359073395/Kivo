from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).parents[1] / "scripts" / "presenter_image_gate.py"
SPEC = importlib.util.spec_from_file_location("presenter_image_gate", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def approved_fixture() -> dict:
    return {
        "verifiedSellingPoints": ["portable stick for tidying baby hairs"],
        "targetAudience": "young adult Indonesian daily hair-styling users",
        "useScenario": "quickly tidying flyaways before leaving home",
        "sourceClassification": "render_or_uncertain",
        "sourceLightingAssessed": True,
        "sourcePerspectiveAssessed": True,
        "canMatchSceneWithoutPackageWarp": True,
        "biomechanics": {
            "limbChainPlausible": True,
            "jointAnglesPlausible": True,
            "gripMechanicallySupported": True,
            "centerOfMassSupported": True,
            "contactAndOcclusionPlausible": True,
        },
        "lighting": {
            "directionMatched": True,
            "colorTemperatureMatched": True,
            "materialReflectionPlausible": True,
            "contactShadowLocalized": True,
        },
        "productFidelity": {
            "packageIdentityLocked": True,
            "generatedLabelUsed": False,
            "placeholderFullyCovered": True,
            "packageGeometryPreserved": True,
        },
    }


class PresenterImageGateTests(unittest.TestCase):
    def test_approved_candidate_still_requires_visual_qa(self) -> None:
        result = MODULE.evaluate_presenter_candidate(approved_fixture())
        self.assertTrue(result["approved"])
        self.assertEqual(result["action"], "approve_presenter_candidate")
        self.assertTrue(result["manualVisualQaStillRequired"])

    def test_missing_audience_brief_stops_random_person_generation(self) -> None:
        payload = approved_fixture()
        payload["targetAudience"] = ""
        self.assertEqual(
            MODULE.evaluate_presenter_candidate(payload)["action"],
            "stop_missing_product_audience_brief",
        )

    def test_unassessed_rendered_source_stops_before_compositing(self) -> None:
        payload = approved_fixture()
        payload["sourceLightingAssessed"] = False
        self.assertEqual(
            MODULE.evaluate_presenter_candidate(payload)["action"],
            "stop_assess_product_source",
        )

    def test_required_package_warp_requests_better_angle(self) -> None:
        payload = approved_fixture()
        payload["canMatchSceneWithoutPackageWarp"] = False
        self.assertEqual(
            MODULE.evaluate_presenter_candidate(payload)["action"],
            "stop_request_better_product_angle",
        )

    def test_impossible_wrist_restarts_from_pose(self) -> None:
        payload = approved_fixture()
        payload["biomechanics"]["jointAnglesPlausible"] = False
        self.assertEqual(
            MODULE.evaluate_presenter_candidate(payload)["action"],
            "reject_and_regenerate_pose",
        )

    def test_bad_contact_shadow_restarts_lighting(self) -> None:
        payload = approved_fixture()
        payload["lighting"]["contactShadowLocalized"] = False
        self.assertEqual(
            MODULE.evaluate_presenter_candidate(payload)["action"],
            "reject_and_regenerate_lighting",
        )

    def test_generated_label_never_enters_final(self) -> None:
        payload = approved_fixture()
        payload["productFidelity"]["generatedLabelUsed"] = True
        self.assertEqual(
            MODULE.evaluate_presenter_candidate(payload)["action"],
            "reject_product_fidelity",
        )


if __name__ == "__main__":
    unittest.main()

