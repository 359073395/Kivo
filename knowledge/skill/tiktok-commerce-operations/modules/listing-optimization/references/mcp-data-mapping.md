# TikTok MCP Capability Discovery and Data Mapping

TikTok Agentic Hub and connected MCP servers can expose different tools, schemas, regions, and permissions over time. Discover capabilities at runtime instead of coding against assumed method names.

## Discovery procedure

1. Search available tools, MCP resources, and resource templates for TikTok, Shop, product, catalog, ads, analytics, creative, and policy capabilities.
2. Inspect tool schemas before calling them.
3. Prefer read-only calls that answer the current field group.
4. Record the server, tool, query scope, retrieval time, and returned field path.
5. If the required field is not exposed, use the fallback artifact column below.
6. Never treat authentication failure as permission to switch to another account or browser session without user authorization.

## Field groups

| Field group | Desired data | Fallback artifact |
|---|---|---|
| Identity | product ID, seller SKU, name, brand, category, status | product URL or Seller Center screenshot |
| Copy | title, description, highlights, attributes | pasted listing text or export |
| Variants | variant IDs, names, price, stock, images | SKU table screenshot or spreadsheet |
| Offer | price, list price, voucher, shipping, gift, deadline | promotion screenshot and selected-variant page |
| Media | image URLs, video, alt metadata | original image files and page screenshots |
| Performance | impressions, clicks, CTR, PDP visits, orders, CVR, GMV, refunds | analytics export or screenshots |
| Ads | creative, caption, product, price, promotion, performance | ad preview, script, caption, or export |
| Policy | category rules, violations, review status | current official policy link or Seller Center notice |

## Provenance record

For publish-critical values, store:

```json
{
  "field": "price.current",
  "value": 99000,
  "source_type": "mcp",
  "source_label": "actual server and tool",
  "retrieved_at": "ISO-8601 timestamp",
  "verified": true,
  "notes": "selected variant context"
}
```

## Conflict handling

Use Seller Center or authorized account data for current operational truth, but still report public-page or ad conflicts. Require human confirmation when a conflict affects price, variant, gift, package contents, product identity, compliance, or image generation.

## No-MCP behavior

The Skill remains functional without MCP. State that live data is unavailable, avoid live-performance conclusions, and ask for the smallest useful export or screenshot.

