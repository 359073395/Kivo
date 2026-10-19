#!/usr/bin/env python3
"""Create a deterministic owned-SKU pre-screen when no live market data exists."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def number(value, default=0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def score(row: dict) -> tuple[float, list[str], list[str]]:
    plus: list[str] = []
    minus: list[str] = []
    value = number(row.get("profile_completeness")) * 40
    if number(row.get("profile_completeness")) >= 0.8:
        plus.append("产品资料相对完整")
    shops = number(row.get("online_shop_count"))
    value += min(shops, 5) / 5 * 20
    if shops:
        plus.append(f"快照中有{int(shops)}个在线店铺")
    cod = str(row.get("cod") or "").strip().casefold()
    cod_is_known = bool(cod) and cod not in {"未知", "待确认", "unknown", "not_available", "n/a", "none", "null", "-"}
    if cod_is_known:
        value += 10
        plus.append("快照中COD有明确值")
    else:
        minus.append("COD未知或待确认")
    if row.get("image_thumbnail"):
        value += 10
        plus.append("有便携产品缩略图")
    if row.get("selling_points"):
        value += 10
        plus.append("有可复核的刊登卖点素材")
    if str(row.get("listed_in_18_shops")) in {"是", "true", "True", "1"}:
        value += 10
        plus.append("18店快照中有上架记录")
    if row.get("conflict_status"):
        value -= 15
        minus.append(f"存在数据冲突：{row['conflict_status']}")
    risks = row.get("claim_risk_tags") or []
    if risks:
        value -= min(30, len(risks) * 8)
        minus.append("刊登话术需审查：" + "、".join(risks))
    if row.get("missing_fields"):
        minus.append(f"资料缺失：{row['missing_fields']}")
    return round(max(0, min(100, value)), 1), plus, minus


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("catalog", type=Path)
    parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.catalog.read_text(encoding="utf-8").splitlines() if line.strip()]
    ranked = []
    for row in rows:
        if not row.get("sku") or not row.get("activity_price_idr") or not row.get("image_thumbnail"):
            continue
        value, plus, minus = score(row)
        ranked.append({
            "sku": row["sku"],
            "preliminary_score": value,
            "status": "preliminary_candidate",
            "decision_pool": "补数据池",
            "not_a_current_recommendation": True,
            "plus_factors": plus,
            "minus_factors": minus,
            "required_next_data": [
                "48小时内TikTok/LinkFox市场证据与商品链接",
                "库存、成本、毛利与保本ROAS",
                "目标店铺当前有效商品链接",
                "当前价格、活动、COD与合规复核",
            ],
        })
    ranked.sort(key=lambda item: (-item["preliminary_score"], item["sku"].casefold()))
    print(json.dumps({
        "mode": "owned_sku_preliminary_without_live_market_data",
        "notice": "仅为内部数据完整度初筛，不代表当前市场推荐；全部进入补数据池。",
        "items": ranked[: max(0, args.limit)],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
