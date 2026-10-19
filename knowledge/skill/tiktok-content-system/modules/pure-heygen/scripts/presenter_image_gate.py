from __future__ import annotations

from typing import Any


SOURCE_CLASSES = {"verified_photo", "edited_cutout", "render_or_uncertain"}


def evaluate_presenter_candidate(payload: dict[str, Any]) -> dict[str, Any]:
    """Return the next image-gate action from auditable candidate metadata.

    This validates the production decision contract. It does not replace visual QA.
    """

    selling_points = payload.get("verifiedSellingPoints")
    if not isinstance(selling_points, list) or not any(str(item).strip() for item in selling_points):
        return _reject("stop_missing_product_audience_brief", "missing_verified_selling_points")
    if not str(payload.get("targetAudience", "")).strip():
        return _reject("stop_missing_product_audience_brief", "missing_target_audience")
    if not str(payload.get("useScenario", "")).strip():
        return _reject("stop_missing_product_audience_brief", "missing_use_scenario")

    source_class = payload.get("sourceClassification")
    if source_class not in SOURCE_CLASSES:
        return _reject("stop_assess_product_source", "unclassified_product_source")
    if payload.get("sourceLightingAssessed") is not True:
        return _reject("stop_assess_product_source", "product_source_lighting_not_assessed")
    if payload.get("sourcePerspectiveAssessed") is not True:
        return _reject("stop_assess_product_source", "product_source_perspective_not_assessed")
    if payload.get("canMatchSceneWithoutPackageWarp") is not True:
        return _reject("stop_request_better_product_angle", "scene_requires_package_warp")

    biomechanics = payload.get("biomechanics") or {}
    for field in (
        "limbChainPlausible",
        "jointAnglesPlausible",
        "gripMechanicallySupported",
        "centerOfMassSupported",
        "contactAndOcclusionPlausible",
    ):
        if biomechanics.get(field) is not True:
            return _reject("reject_and_regenerate_pose", f"biomechanics_failed:{field}")

    lighting = payload.get("lighting") or {}
    for field in (
        "directionMatched",
        "colorTemperatureMatched",
        "materialReflectionPlausible",
        "contactShadowLocalized",
    ):
        if lighting.get(field) is not True:
            return _reject("reject_and_regenerate_lighting", f"lighting_failed:{field}")

    fidelity = payload.get("productFidelity") or {}
    if fidelity.get("packageIdentityLocked") is not True:
        return _reject("reject_product_fidelity", "package_identity_not_locked")
    if fidelity.get("generatedLabelUsed") is not False:
        return _reject("reject_product_fidelity", "generated_label_used")
    if fidelity.get("placeholderFullyCovered") is not True:
        return _reject("reject_product_fidelity", "placeholder_not_fully_covered")
    if fidelity.get("packageGeometryPreserved") is not True:
        return _reject("reject_product_fidelity", "package_geometry_not_preserved")

    return {
        "approved": True,
        "action": "approve_presenter_candidate",
        "reasons": [],
        "manualVisualQaStillRequired": True,
    }


def _reject(action: str, reason: str) -> dict[str, Any]:
    return {
        "approved": False,
        "action": action,
        "reasons": [reason],
        "manualVisualQaStillRequired": True,
    }

