"""Read-only selection evidence gate, not ranking or business approval.

Input JSON:
  window: {start_date: YYYY-MM-DD, end_date: YYYY-MM-DD,
           utc_offset_minutes: integer}
  actual_query: {start_epoch: integer seconds, end_epoch: integer seconds}
  competitors: [{id: string, sales7d: number|null,
                 use_as_hot_comparator: bool, product_form_verified: bool}]
  videos: [{id: string, create_epoch: integer seconds,
            availability: available|unavailable|unverified,
            gmv_currency: string|null, gmv_unit: string|null}]
  ranking_metric: views|gmv (optional, defaults to views)
  research (optional): {requested_queries: [string],
    raw_query_results: [{query: string, source_ref: string,
      status: success|empty|failed, products: [object]}],
    claimed_covered_queries: integer (optional),
    claimed_product_count: integer (optional)}

Normalize values from actual responses, not inference. A working URL cannot
certify watching, transcription, learning or own-SKU fit. Supply the project's
UTC offset; for periods with offset transitions, convert each boundary upstream
instead of using this fixed-offset helper.
"""

import argparse
import json
import math
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path


def validate_research_coverage(research):
    """Check raw per-query coverage; summaries and failures are not evidence."""
    requested = research.get("requested_queries", [])
    errors = []
    if (not isinstance(requested, list) or not requested
            or any(not isinstance(q, str) or not q.strip() for q in requested)):
        requested = []
        errors.append("requested_queries_missing_or_invalid")
    requested_set = set(requested)
    if len(requested_set) != len(requested):
        errors.append("duplicate_requested_queries")
    covered, seen = set(), set()
    count = 0
    for row in research.get("raw_query_results", []):
        query = row.get("query")
        if not isinstance(query, str) or query not in requested_set:
            errors.append("raw_query_not_requested_or_missing")
            continue
        if query in seen:
            errors.append("duplicate_raw_query:" + query)
            continue
        seen.add(query)
        source = row.get("source_ref")
        products = row.get("products")
        if not isinstance(source, str) or not source.strip():
            errors.append("raw_source_missing:" + query)
            continue
        if not isinstance(products, list):
            errors.append("raw_products_missing:" + query)
            continue
        status = row.get("status")
        if status == "failed":
            errors.append("query_failed_not_zero_sales:" + query)
            continue
        if status not in ("success", "empty") or (status == "success") != bool(products):
            errors.append("raw_query_status_inconsistent:" + query)
            continue
        covered.add(query)
        count += len(products)
    missing = sorted(requested_set - covered)
    if missing:
        errors.append("requested_query_coverage_incomplete")
    for field, observed in (("claimed_covered_queries", len(covered)),
                            ("claimed_product_count", count)):
        if field in research and (type(research[field]) is not int or research[field] != observed):
            errors.append(field + "_does_not_match_raw_results")
    return {"requested_query_count": len(requested_set),
            "verified_query_count": len(covered), "raw_product_count": count,
            "missing_queries": missing, "errors": errors, "passed": not errors,
            "empty_result_proves_zero_market_sales": False,
            "semantic_fit_or_channel_attribution_certified": False}


def expected_window(window):
    offset = window["utc_offset_minutes"]
    if type(offset) is not int or not -840 <= offset <= 840:
        raise ValueError("utc_offset_minutes must be an explicit valid integer offset")
    start = date.fromisoformat(window["start_date"])
    end = date.fromisoformat(window["end_date"])
    if start > end:
        raise ValueError("start_date must not follow end_date")
    tz = timezone(timedelta(minutes=offset))
    return (int(datetime.combine(start, time.min, tz).timestamp()),
            int(datetime.combine(end + timedelta(days=1), time.min, tz).timestamp()) - 1)


def validate(payload):
    start, end = expected_window(payload["window"])
    query = payload.get("actual_query", {})
    query_ok = (type(query.get("start_epoch")) is int
                and type(query.get("end_epoch")) is int
                and query["start_epoch"] == start and query["end_epoch"] == end)
    errors = [] if query_ok else ["actual_query_window_mismatch_or_unverified"]
    research = None
    if "research" in payload:
        research = validate_research_coverage(payload["research"])
        errors.extend(research["errors"])
    metric = payload.get("ranking_metric", "views")
    if metric not in ("views", "gmv"):
        raise ValueError("ranking_metric must be views or gmv")
    competitors, videos = [], []
    if not payload.get("competitors") and not payload.get("videos"):
        errors.append("no_evidence_records")
    for row in payload.get("competitors", []):
        sales = row.get("sales7d")
        numeric = (type(sales) in (int, float) and math.isfinite(sales) and sales >= 0)
        positive = numeric and sales > 0
        comparable = row.get("product_form_verified") is True
        reasons = []
        if not isinstance(row.get("id"), str) or not row["id"].strip():
            errors.append("competitor_id_missing_or_not_text")
        if type(row.get("use_as_hot_comparator")) is not bool:
            errors.append("competitor_evidence_role_unverified")
        if not numeric:
            reasons.append("sales_unknown_or_invalid")
        elif sales == 0:
            reasons.append("zero_sales_is_not_hot_sales_evidence")
        if not comparable:
            reasons.append("product_form_not_verified")
        if row.get("use_as_hot_comparator") is True and not (positive and comparable):
            errors.append("invalid_hot_comparator:" + str(row.get("id")))
        competitors.append({"id": row.get("id"),
                            "usable_as_hot_comparator": positive and comparable,
                            "reasons": reasons})
    seen = set()
    for row in payload.get("videos", []):
        ident, epoch = row.get("id"), row.get("create_epoch")
        reasons = []
        valid_id = isinstance(ident, str) and bool(ident.strip())
        if not valid_id:
            reasons.append("id_missing_or_not_text")
        elif ident in seen:
            reasons.append("duplicate_video_id")
        else:
            seen.add(ident)
        if not query_ok:
            reasons.append("query_window_unverified")
        if type(epoch) is not int or not start <= epoch <= end:
            reasons.append("date_missing_or_outside_window")
        availability = row.get("availability", "unverified")
        if availability == "unavailable":
            reasons.append("known_unavailable")
        elif availability not in ("available", "unverified"):
            reasons.append("invalid_availability")
        if metric == "gmv" and not all(isinstance(row.get(k), str) and row[k].strip()
                                        for k in ("gmv_currency", "gmv_unit")):
            reasons.append("gmv_currency_or_unit_missing")
        videos.append({"id": ident, "usable_metadata": not reasons,
                       "page_verified": availability == "available", "reasons": reasons})
    if metric == "gmv":
        bases = {(str(r.get("gmv_currency", "")).strip(), str(r.get("gmv_unit", "")).strip())
                 for r in payload.get("videos", [])}
        if len(bases) > 1:
            errors.append("mixed_gmv_bases_require_verified_normalization")
    return {"test_type": "deterministic_metadata_gate",
            "expected_query": {"start_epoch": start, "end_epoch": end},
            "query_verified": query_ok, "competitors": competitors, "videos": videos,
            "research_coverage": research,
            "usable_video_metadata_count": sum(v["usable_metadata"] for v in videos),
            "errors": errors, "passed": not errors and all(v["usable_metadata"] for v in videos),
            "semantic_behavior_certified": False, "content_learning_certified": False,
            "formal_test_or_scale_authorized": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    result = validate(json.loads(args.input.read_text(encoding="utf-8-sig")))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
