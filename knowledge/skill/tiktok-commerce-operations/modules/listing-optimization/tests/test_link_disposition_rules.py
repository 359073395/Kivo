import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).parents[1] / "scripts" / "classify_link_disposition.py"
SPEC = importlib.util.spec_from_file_location("classify_link_disposition", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class LinkDispositionRulesTest(unittest.TestCase):
    def test_review_rejection_prohibits_listing(self):
        result = MODULE.classify_link_disposition(
            execution_status="不通过",
            has_valid_new_id=False,
            observation_window_complete=True,
            orders=0,
        )
        self.assertEqual(result, "prohibit_listing")

    def test_zero_orders_alone_never_imply_deletion(self):
        result = MODULE.classify_link_disposition(
            execution_status="完成",
            has_valid_new_id=True,
            observation_window_complete=True,
            orders=0,
        )
        self.assertEqual(result, "insufficient_data")

    def test_beau_positive_signals_are_retained(self):
        result = MODULE.classify_link_disposition(
            execution_status="完成", has_valid_new_id=True,
            observation_window_complete=True, orders=0,
            views=4240, clicks=31, cart_rate=0.0417, ad_clicks=0,
        )
        self.assertEqual(result, "retain_and_assess")

    def test_ad_clicks_are_not_ignored(self):
        result = MODULE.classify_link_disposition(
            execution_status="完成", has_valid_new_id=True,
            observation_window_complete=True, orders=0,
            views=74, clicks=0, cart_rate=0, ad_clicks=2,
        )
        self.assertEqual(result, "retain_and_assess")

    def test_verified_all_zero_only_becomes_review_candidate(self):
        result = MODULE.classify_link_disposition(
            execution_status="完成", has_valid_new_id=True,
            observation_window_complete=True, orders=0,
            views=0, clicks=0, cart_rate=0, ad_clicks=0,
            data_verified=True, fully_saleable=True,
        )
        self.assertEqual(result, "review_low_signal_link")

    def test_unverified_zero_data_requires_verification(self):
        result = MODULE.classify_link_disposition(
            execution_status="完成", has_valid_new_id=True,
            observation_window_complete=True, orders=0,
            views=0, clicks=0, cart_rate=0, ad_clicks=0,
        )
        self.assertEqual(result, "retain_and_verify")

    def test_completed_link_with_order_is_retained_for_optimization(self):
        result = MODULE.classify_link_disposition(
            execution_status="完成",
            has_valid_new_id=True,
            observation_window_complete=True,
            orders=1,
        )
        self.assertEqual(result, "retain_and_optimize")

    def test_incomplete_window_is_not_deleted(self):
        result = MODULE.classify_link_disposition(
            execution_status="完成",
            has_valid_new_id=True,
            observation_window_complete=False,
            orders=0,
        )
        self.assertEqual(result, "insufficient_data")


if __name__ == "__main__":
    unittest.main()
