#!/usr/bin/env python3
"""Calculate a deterministic Indonesian TikTok Shop listing-readiness score."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


RUBRIC = {
    "conversion": {
        "label": "Conversion readiness",
        "weight": 30,
        "checks": [
            "primary_value_clear",
            "benefit_supported",
            "use_case_clear",
            "key_specs_visible",
            "package_contents_clear",
            "variant_choice_clear",
            "how_to_use_clear",
            "objections_addressed",
            "purchase_path_clear",
            "mobile_scan_friendly",
        ],
    },
    "search": {
        "label": "Search and title",
        "weight": 20,
        "checks": [
            "product_type_present",
            "primary_keyword_early",
            "secondary_keywords_natural",
            "title_matches_product",
            "category_specificity",
            "attributes_complete",
            "variant_terms_consistent",
            "no_keyword_stuffing",
            "indonesian_search_language",
            "keyword_evidence_available",
        ],
    },
    "click": {
        "label": "Image and click appeal",
        "weight": 15,
        "checks": [
            "product_dominant",
            "background_clear",
            "mobile_legible",
            "visual_hierarchy",
            "key_differentiator_visible",
        ],
    },
    "trust": {
        "label": "Information and trust",
        "weight": 15,
        "checks": [
            "brand_identity_consistent",
            "factual_claims",
            "specs_consistent",
            "package_contents_consistent",
            "proof_or_limitations_clear",
        ],
    },
    "price_sku": {
        "label": "Price, promotion, and SKU",
        "weight": 10,
        "checks": [
            "price_visible_consistent",
            "promotion_truthful",
            "variants_clear",
            "bundle_value_clear",
            "value_context_clear",
        ],
    },
    "ad_alignment": {
        "label": "Ad-to-listing alignment",
        "weight": 10,
        "checks": [
            "product_identity_match",
            "price_promo_match",
            "claim_match",
            "variant_gift_match",
            "creative_landing_message_match",
        ],
    },
}

ALLOWED_VALUES = {0.0, 0.5, 1.0}
COMPLIANCE_STATUSES = {"pass", "low", "medium", "high", "needs_review"}


def full_check_id(dimension: str, check: str) -> str:
    return f"{dimension}.{check}"


def parse_entry(raw: Any, check_id: str) -> tuple[float | None, list[str]]:
    if isinstance(raw, dict):
        value = raw.get("value")
        evidence_raw = raw.get("evidence", [])
    else:
        value = raw
        evidence_raw = []

    if evidence_raw is None:
        evidence = []
    elif isinstance(evidence_raw, list):
        evidence = [str(item) for item in evidence_raw if str(item).strip()]
    else:
        evidence = [str(evidence_raw)]

    if value is None:
        return None, evidence
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{check_id}: value must be 0, 0.5, 1, or null")
    value = float(value)
    if value not in ALLOWED_VALUES:
        raise ValueError(f"{check_id}: value must be 0, 0.5, 1, or null")
    return value, evidence


def calculate(assessment: dict[str, Any]) -> dict[str, Any]:
    checks = assessment.get("checks", {})
    if not isinstance(checks, dict):
        raise ValueError("assessment.checks must be an object")

    not_applicable_raw = assessment.get("not_applicable_dimensions", [])
    if not isinstance(not_applicable_raw, list):
        raise ValueError("assessment.not_applicable_dimensions must be a list")
    not_applicable = {str(item) for item in not_applicable_raw}
    unknown_dimensions = sorted(not_applicable - set(RUBRIC))
    if unknown_dimensions:
        raise ValueError(f"Unknown not-applicable dimensions: {unknown_dimensions}")

    known_ids = {
        full_check_id(dimension, check)
        for dimension, config in RUBRIC.items()
        for check in config["checks"]
    }
    extra_ids = sorted(set(checks) - known_ids)

    total_score = 0.0
    total_checks = 0
    known_checks = 0
    evidenced_checks = 0
    applicable_max_score = 0.0
    dimensions: dict[str, Any] = {}

    for dimension, config in RUBRIC.items():
        if dimension in not_applicable:
            dimensions[dimension] = {
                "label": config["label"],
                "score": None,
                "max_score": config["weight"],
                "status": "not_applicable",
                "checks": [],
            }
            continue

        applicable_max_score += config["weight"]
        check_results = []
        earned = 0.0
        per_check = config["weight"] / len(config["checks"])
        for check in config["checks"]:
            check_id = full_check_id(dimension, check)
            value, evidence = parse_entry(checks.get(check_id), check_id)
            total_checks += 1
            if value is not None:
                known_checks += 1
                earned += per_check * value
                if evidence:
                    evidenced_checks += 1
            check_results.append(
                {
                    "id": check_id,
                    "value": value,
                    "max_points": round(per_check, 4),
                    "earned_points": round(per_check * (value or 0), 4),
                    "evidence": evidence,
                }
            )
        total_score += earned
        dimensions[dimension] = {
            "label": config["label"],
            "score": round(earned, 2),
            "max_score": config["weight"],
            "checks": check_results,
        }

    if applicable_max_score <= 0:
        raise ValueError("At least one scoring dimension must be applicable")

    normalized_score = 100 * total_score / applicable_max_score

    compliance = assessment.get("compliance", {})
    if not isinstance(compliance, dict):
        raise ValueError("assessment.compliance must be an object")
    status = compliance.get("status", "needs_review")
    if status not in COMPLIANCE_STATUSES:
        raise ValueError(f"compliance.status must be one of {sorted(COMPLIANCE_STATUSES)}")
    gate = {
        "pass": "clear",
        "low": "warning",
        "medium": "revise_before_publish",
        "high": "blocked",
        "needs_review": "manual_review_required",
    }[status]

    return {
        "score_version": "1.0",
        "total_score": round(normalized_score, 2),
        "max_score": 100,
        "estimated_content_readiness": round(normalized_score, 2),
        "applicable_raw_score": round(total_score, 2),
        "applicable_max_score": round(applicable_max_score, 2),
        "data_coverage_percent": round(100 * known_checks / total_checks, 2),
        "evidence_coverage_percent": round(100 * evidenced_checks / total_checks, 2),
        "publishing_gate": gate,
        "compliance": {
            "status": status,
            "issues": compliance.get("issues", []),
        },
        "dimensions": dimensions,
        "unknown_check_count": total_checks - known_checks,
        "not_applicable_dimensions": sorted(not_applicable),
        "extra_check_ids": extra_ids,
        "notes": assessment.get("notes", []),
    }


def self_test() -> None:
    all_checks = {
        full_check_id(dimension, check): {"value": 1, "evidence": ["verified"]}
        for dimension, config in RUBRIC.items()
        for check in config["checks"]
    }
    perfect = calculate({"checks": all_checks, "compliance": {"status": "pass"}})
    assert perfect["total_score"] == 100
    assert perfect["data_coverage_percent"] == 100
    assert perfect["publishing_gate"] == "clear"

    empty = calculate({"checks": {}, "compliance": {"status": "high", "issues": ["claim"]}})
    assert empty["total_score"] == 0
    assert empty["unknown_check_count"] == 40
    assert empty["publishing_gate"] == "blocked"

    new_product = calculate(
        {
            "checks": all_checks,
            "not_applicable_dimensions": ["ad_alignment"],
            "compliance": {"status": "pass"},
        }
    )
    assert new_product["total_score"] == 100
    assert new_product["applicable_max_score"] == 90
    assert new_product["dimensions"]["ad_alignment"]["status"] == "not_applicable"
    print("score-listing self-test: OK")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assessment", type=Path, help="Assessment JSON")
    parser.add_argument("--out", type=Path, help="Score JSON output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return
    if not args.assessment or not args.out:
        parser.error("--assessment and --out are required unless --self-test is used")

    assessment = json.loads(args.assessment.read_text(encoding="utf-8"))
    if not isinstance(assessment, dict):
        raise SystemExit("Assessment JSON must be an object")
    result = calculate(assessment)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
