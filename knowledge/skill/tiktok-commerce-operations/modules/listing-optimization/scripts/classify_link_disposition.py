from __future__ import annotations


def classify_link_disposition(
    *,
    execution_status: str,
    has_valid_new_id: bool,
    observation_window_complete: bool,
    orders: int | None,
    views: int | None = None,
    clicks: int | None = None,
    cart_rate: float | None = None,
    ad_clicks: int | None = None,
    data_verified: bool = False,
    fully_saleable: bool = False,
) -> str:
    """Conservative triage only; never authorize platform deletion."""
    if execution_status == "不通过":
        return "prohibit_listing"
    if execution_status == "未开始" or not has_valid_new_id:
        return "pending_test"
    if not observation_window_complete or orders is None:
        return "insufficient_data"
    if orders > 0:
        return "retain_and_optimize"
    signals = (clicks, cart_rate, ad_clicks)
    if any(value is not None and value > 0 for value in signals):
        return "retain_and_assess"
    if views is None or any(value is None for value in signals):
        return "insufficient_data"
    if data_verified and fully_saleable and views == 0 and all(value == 0 for value in signals):
        return "review_low_signal_link"
    return "retain_and_verify"
