"""Synthetic regression for observed metadata failures; no network/private data."""
import copy
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_market_evidence import expected_window, validate, validate_research_coverage


class MarketEvidenceTests(unittest.TestCase):
    def test_summary_claim_of_30_queries_60_products_does_not_replace_raw_results(self):
        result = validate_research_coverage({
            "requested_queries": ["function-" + str(i) for i in range(30)],
            "raw_query_results": [{"query": "function-0", "source_ref": "raw.json",
                                   "status": "success", "products": [{"id": "one"}, {"id": "two"}]}],
            "claimed_covered_queries": 30, "claimed_product_count": 60})
        self.assertFalse(result["passed"])
        self.assertEqual(result["verified_query_count"], 1)
        self.assertEqual(result["raw_product_count"], 2)
        self.assertEqual(len(result["missing_queries"]), 29)

    def test_true_empty_search_is_coverage_but_not_zero_sales(self):
        result = validate_research_coverage({
            "requested_queries": ["function"],
            "raw_query_results": [{"query": "function", "source_ref": "raw.json",
                                   "status": "empty", "products": []}]})
        self.assertTrue(result["passed"])
        self.assertFalse(result["empty_result_proves_zero_market_sales"])

    def test_failed_or_unsourced_search_cannot_be_reported_as_empty(self):
        for status, source in (("failed", "raw.json"), ("empty", "")):
            result = validate_research_coverage({
                "requested_queries": ["function"],
                "raw_query_results": [{"query": "function", "source_ref": source,
                                       "status": status, "products": []}]})
            self.assertFalse(result["passed"])
            self.assertEqual(result["verified_query_count"], 0)

    def test_duplicate_query_results_do_not_inflate_coverage(self):
        row = {"query": "function", "source_ref": "raw.json",
               "status": "success", "products": [{"id": "one"}]}
        result = validate_research_coverage({
            "requested_queries": ["function", "other"],
            "raw_query_results": [row, copy.deepcopy(row)]})
        self.assertFalse(result["passed"])
        self.assertEqual(result["verified_query_count"], 1)
        self.assertEqual(result["raw_product_count"], 1)

    def payload(self):
        return {"window": {"start_date": "2026-06-07", "end_date": "2026-09-04",
                           "utc_offset_minutes": 420},
                "actual_query": {"start_epoch": 1780765200, "end_epoch": 1788541199},
                "competitors": [{"id": "example-product", "sales7d": 10,
                                 "use_as_hot_comparator": True, "product_form_verified": True}],
                "videos": [{"id": "example-video", "create_epoch": 1780765200,
                            "availability": "unverified"}]}

    def test_exact_jakarta_window(self):
        self.assertEqual(expected_window(self.payload()["window"]), (1780765200, 1788541199))

    def test_known_bad_query_never_certified(self):
        p = self.payload()
        p["actual_query"] = {"start_epoch": 1775494800, "end_epoch": 1783270799}
        r = validate(p)
        self.assertFalse(r["passed"])
        self.assertEqual(r["usable_video_metadata_count"], 0)

    def test_period_boundaries_and_millisecond_rejection(self):
        for epoch, expected in ((1780765200, True), (1788541199, True),
                                (1780765199, False), (1788541200, False),
                                (1780765200000, False)):
            p = self.payload()
            p["videos"][0]["create_epoch"] = epoch
            self.assertEqual(validate(p)["passed"], expected)

    def test_zero_unknown_and_invalid_sales_cannot_prove_hot(self):
        for sales in (0, None, -1, True, float("nan"), "10"):
            p = self.payload()
            p["competitors"][0]["sales7d"] = sales
            self.assertFalse(validate(p)["passed"])

    def test_zero_sales_can_be_kept_as_negative_reference(self):
        p = self.payload()
        p["competitors"][0].update(sales7d=0, use_as_hot_comparator=False)
        r = validate(p)
        self.assertTrue(r["passed"])
        self.assertFalse(r["competitors"][0]["usable_as_hot_comparator"])

    def test_known_unavailable_and_duplicate_video_excluded(self):
        p = self.payload()
        p["videos"][0]["availability"] = "unavailable"
        self.assertEqual(validate(p)["usable_video_metadata_count"], 0)
        p = self.payload()
        p["videos"].append(copy.deepcopy(p["videos"][0]))
        r = validate(p)
        self.assertFalse(r["passed"])
        self.assertEqual(r["usable_video_metadata_count"], 1)

    def test_metadata_does_not_certify_learning_or_permission(self):
        r = validate(self.payload())
        self.assertTrue(r["passed"])
        self.assertFalse(r["videos"][0]["page_verified"])
        self.assertFalse(r["semantic_behavior_certified"])
        self.assertFalse(r["content_learning_certified"])
        self.assertFalse(r["formal_test_or_scale_authorized"])

    def test_gmv_missing_units_cannot_rank(self):
        p = self.payload()
        p["ranking_metric"] = "gmv"
        self.assertFalse(validate(p)["passed"])
        p["videos"][0].update(gmv_currency="IDR", gmv_unit="currency_units")
        self.assertTrue(validate(p)["passed"])

    def test_previous_test_flag_does_not_exclude_product(self):
        p = self.payload()
        p["competitors"][0]["previously_tested"] = True
        self.assertTrue(validate(p)["passed"])

    def test_comparability_not_inferred_from_sales(self):
        p = self.payload()
        p["competitors"][0]["product_form_verified"] = False
        self.assertFalse(validate(p)["passed"])

    def test_empty_evidence_not_passed(self):
        p = self.payload()
        p["competitors"], p["videos"] = [], []
        self.assertFalse(validate(p)["passed"])

    def test_missing_competitor_role_is_not_silently_reference(self):
        p = self.payload()
        del p["competitors"][0]["use_as_hot_comparator"]
        self.assertFalse(validate(p)["passed"])

    def test_mixed_gmv_bases_block_ranking(self):
        p = self.payload()
        p["ranking_metric"] = "gmv"
        p["videos"][0].update(gmv_currency="IDR", gmv_unit="currency_units")
        other = copy.deepcopy(p["videos"][0])
        other.update(id="another-video", gmv_currency="USD")
        p["videos"].append(other)
        self.assertFalse(validate(p)["passed"])

    def test_input_is_preserved(self):
        p = self.payload()
        before = copy.deepcopy(p)
        validate(p)
        self.assertEqual(p, before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
