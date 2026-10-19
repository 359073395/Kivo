from __future__ import annotations

from decimal import Decimal


def apply_confirmed_y_sku_aliases(
    primary_prices: dict[str, Decimal],
    alias_source_prices: dict[str, Decimal],
    confirmed_aliases: dict[str, str],
) -> dict[str, Decimal]:
    """Add only explicit one-to-one aliases; never perform fuzzy matching."""
    result = dict(primary_prices)
    for store_sku, warehouse_sku in confirmed_aliases.items():
        if warehouse_sku not in alias_source_prices:
            raise KeyError(
                f"Confirmed Y SKU alias target has no activity price: "
                f"{store_sku} -> {warehouse_sku}"
            )
        alias_price = alias_source_prices[warehouse_sku]
        if store_sku in result and result[store_sku] != alias_price:
            raise ValueError(
                f"Confirmed Y SKU alias conflicts with primary exact price: "
                f"{store_sku}"
            )
        result[store_sku] = alias_price
    return result


def apply_y_platform_activity_fallback(
    candidate: Decimal,
    source: str,
    safety_line: Decimal,
    normalized_skus: list[str],
    y_platform_prices: dict[str, Decimal],
) -> tuple[Decimal | None, str, str | None]:
    """Resolve the approved fallback without rechecking the Y platform price."""
    if candidate < safety_line:
        return candidate, source, None
    if len(normalized_skus) == 1 and normalized_skus[0] in y_platform_prices:
        return (
            y_platform_prices[normalized_skus[0]],
            "y_platform_activity_fallback",
            None,
        )
    return (
        None,
        source,
        "candidate is not below safety line and exact Y platform activity price "
        "is unavailable or ambiguous; ask user",
    )
