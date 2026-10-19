from decimal import Decimal
from pathlib import Path
import sys
import unittest


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from flash_price_rules import (
    apply_confirmed_y_sku_aliases,
    apply_y_platform_activity_fallback,
)


class FlashPriceFallbackTests(unittest.TestCase):
    def test_only_confirmed_alias_is_added(self) -> None:
        result = apply_confirmed_y_sku_aliases(
            {"exact-sku": Decimal("40000")},
            {"hk foot paste 足贴": Decimal("45380")},
            {"hk foot paste": "hk foot paste 足贴"},
        )
        self.assertEqual(result["hk foot paste"], Decimal("45380"))
        self.assertNotIn("similar foot patch", result)

    def test_confirmed_alias_cannot_override_conflicting_exact_price(self) -> None:
        with self.assertRaises(ValueError):
            apply_confirmed_y_sku_aliases(
                {"hk foot paste": Decimal("45000")},
                {"hk foot paste 足贴": Decimal("45380")},
                {"hk foot paste": "hk foot paste 足贴"},
            )

    def test_candidate_below_line_is_unchanged(self) -> None:
        result = apply_y_platform_activity_fallback(
            Decimal("49000"), "main_price", Decimal("50000"),
            ["sku-a"], {"sku-a": Decimal("60000")},
        )
        self.assertEqual(result, (Decimal("49000"), "main_price", None))

    def test_y_price_above_line_is_still_final(self) -> None:
        result = apply_y_platform_activity_fallback(
            Decimal("55000"), "main_price", Decimal("50000"),
            ["sku-a"], {"sku-a": Decimal("60000")},
        )
        self.assertEqual(
            result, (Decimal("60000"), "y_platform_activity_fallback", None),
        )

    def test_y_price_equal_to_line_is_still_final(self) -> None:
        result = apply_y_platform_activity_fallback(
            Decimal("50000"), "old_product_price", Decimal("50000"),
            ["sku-a"], {"sku-a": Decimal("50000")},
        )
        self.assertEqual(
            result, (Decimal("50000"), "y_platform_activity_fallback", None),
        )

    def test_missing_exact_y_price_requires_user(self) -> None:
        candidate, source, blocker = apply_y_platform_activity_fallback(
            Decimal("55000"), "main_price", Decimal("50000"), ["sku-a"], {},
        )
        self.assertIsNone(candidate)
        self.assertEqual(source, "main_price")
        self.assertIn("ask user", blocker or "")

    def test_multiple_skus_require_user(self) -> None:
        candidate, _, blocker = apply_y_platform_activity_fallback(
            Decimal("55000"), "main_price", Decimal("50000"),
            ["sku-a", "sku-b"],
            {"sku-a": Decimal("40000"), "sku-b": Decimal("45000")},
        )
        self.assertIsNone(candidate)
        self.assertIn("ask user", blocker or "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
