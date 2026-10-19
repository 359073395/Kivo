---
name: optimize-tiktok-id-listing
description: Audit and optimize Indonesian TikTok Shop product listings with conversion-first scoring, Indonesian copy, ad-to-listing consistency checks, and diagnosis-driven product image editing or generation. Use when Codex needs to improve a TikTok Shop Indonesia product link, SKU, title, description, keywords, attributes, pricing presentation, variants, product images, or ad landing consistency; when the user provides a product URL, screenshots, seller exports, spreadsheets, MCP data, or original product photos; or when the user asks in Chinese or English to 优化 TikTok 商品链接、商品卡、主图、详情页、转化率、搜索曝光、印尼语文案或广告承接.
---

# Optimize Indonesian TikTok Shop Listings

Diagnose evidence first, then produce traceable listing and image improvements. Prefer live authorized data, but remain useful with URLs, screenshots, spreadsheets, or manually supplied facts.

## Choose the operating mode

- Use **full optimization** by default: diagnose, score, rewrite copy, create justified image tasks, and execute image edits when valid source images and image tools are available.
- Use **audit only** when the user asks only for analysis, scoring, or recommendations.
- Use **image execution only** when an approved diagnosis and image-task specification already exist. Do not invent new visual objectives in this mode.

## Enforce non-negotiable rules

- Separate verified facts, user claims, inferences, and missing data.
- Never fabricate search volume, competitor metrics, platform limits, sales performance, certifications, product effects, discounts, gifts, variants, or package contents.
- Treat compliance as a publishing gate, not a score that other strengths can offset.
- Preserve product shape, structure, packaging, color, logo, model, specifications, labels, and accessory count in image work.
- Do not overwrite source images or automatically upload, publish, or modify a live listing or ad.
- Use `gpt-image-2` for every image generation and edit performed by this Skill. Do not silently use or downgrade to another image model.
- Describe the post-optimization score as **estimated content readiness**, never as promised sales growth.
- Prioritize current official TikTok rules and actual MCP tool schemas over static references.

## Workflow

### 1. Collect evidence

Accept any combination of:

- TikTok Shop product URL or product identifier
- TikTok MCP data from authorized tools
- Seller Center screenshots or exports
- CSV, XLSX, JSON, or pasted listing data
- original product and packaging images
- ad creative, script, caption, price, gift, and offer details
- performance data such as impressions, CTR, product-page visits, CVR, GMV, and refund rate

Record the source of every important field. If a source cannot be read, request the smallest missing artifact needed to continue and still complete all unblocked work.

### 2. Discover MCP capabilities

Read [references/mcp-data-mapping.md](references/mcp-data-mapping.md). Discover available TikTok tools and their schemas at runtime. Do not assume a fixed server name, method name, field name, region, or permission.

Use MCP only for authorized read operations unless the user explicitly requests and authorizes a state-changing operation. This Skill's default workflow remains read-only.

### 3. Normalize product data

Consolidate extracted facts into one JSON object and run:

```bash
python scripts/normalize-product-data.py --input raw-product.json --out normalized-product.json
```

The normalized object must retain field provenance and source conflicts. Do not silently resolve a conflict between Seller Center data, a public page, an ad, and a user statement.

### 4. Run the compliance gate

Read [references/indonesia-market-rules.md](references/indonesia-market-rules.md). Classify each issue as:

- `low`: warn and continue
- `medium`: revise before treating output as publish-ready
- `high`: stop generating the affected claim or image
- `needs_review`: evidence is insufficient for an automated conclusion

Do not present this operational review as legal advice or an official TikTok approval.

### 5. Diagnose the listing

Evaluate:

- search intent, title, keywords, category, attributes, and variants
- mobile first-frame clarity and click appeal
- value proposition, benefits, specifications, usage, package contents, objections, and trust
- price, promotion, bundle, and SKU clarity
- Indonesian localization and natural phrasing
- ad-to-listing identity, price, offer, claim, variant, gift, and message alignment

Read the domain references only when relevant:

- [references/listing-scoring-rubric.md](references/listing-scoring-rubric.md)
- [references/indonesia-copywriting.md](references/indonesia-copywriting.md)
- [references/ads-listing-alignment.md](references/ads-listing-alignment.md)

For every finding, record: issue ID, evidence, funnel stage, severity, recommendation, and success signal.

### 6. Score deterministically

Create an assessment JSON using the exact check IDs in [references/listing-scoring-rubric.md](references/listing-scoring-rubric.md). Set each check to `1`, `0.5`, `0`, or `null`, with evidence.

For a genuine new product with no ad or ad campaign yet, set `"not_applicable_dimensions": ["ad_alignment"]`. Do not mark the ad dimension as zero or unknown merely because no ad exists. The scorer normalizes the applicable dimensions to 100. If an ad exists but was not supplied, keep the dimension applicable and use `null` checks.

Run:

```bash
python scripts/score-listing.py --assessment before-assessment.json --out before-score.json
```

After optimization, create a second assessment and run the same command. Compare the two JSON results. Missing or unknown checks count as not ready and reduce evidence coverage; do not award assumed points.

Never emit an exact score that was not produced by `scripts/score-listing.py`. Score the current evidence and completed deliverables only. Do not award after-score points for a recommendation, reshoot brief, image task, unverified specification, or other work that has not been executed and validated. In audit-only mode, show the current score and mark the after score as `not scored`; describe upside qualitatively instead of inventing a projected total.

### 7. Generate Indonesian copy

Follow [references/indonesia-copywriting.md](references/indonesia-copywriting.md). Produce:

- one recommended title and two alternatives
- concise benefit-led highlights
- a structured product description
- missing attribute and variant recommendations
- evidence-backed keyword groups
- excluded or risky terms

Explain reasoning in Chinese by default when the user speaks Chinese. Keep customer-facing copy in natural Bahasa Indonesia and add Chinese glosses only when useful.

Keep the **ready-to-use** copy free of placeholders, brackets, asterisks, and unverified claims. If a missing fact prevents a section from being publish-ready, omit that claim or section from the safe version and list it separately under `Missing facts / optional draft after verification`. Never mix unverified specifications into a recommended title, highlight, or final description merely by adding a footnote.

### 8. Convert visual recommendations into image tasks

Read [references/image-optimization-workflow.md](references/image-optimization-workflow.md).

Create an image task only when a diagnosed issue requires a visual change. Each task must contain:

- linked issue ID and evidence
- edit target and roles of all input images
- business objective and funnel stage
- allowed changes
- invariants that must remain unchanged
- exact Indonesian text, if any
- prohibited claims or objects
- measurable acceptance criteria
- versioned output filename

Do not generate a fixed number of images. Keep images that already satisfy the recommendation unchanged.

### 9. Execute and validate image work

When raster image creation or editing is required, invoke the available `imagegen` skill and use its CLI/API model-control path with `gpt-image-2`. The built-in path must not be used when it cannot confirm the model.

- Treat an existing product image as an **edit target**, not merely a style reference.
- Use the bundled imagegen CLI at `$CODEX_HOME/skills/.system/imagegen/scripts/image_gen.py`; do not create or modify a custom API runner.
- Pass `--model gpt-image-2` explicitly for both `generate` and `edit`, even though it is the CLI default.
- Require `OPENAI_API_KEY` in the local environment for live generation. Never ask the user to paste the key in chat.
- Do not pass `--input-fidelity`; `gpt-image-2` always uses high fidelity for image inputs.
- Use one CLI job per distinct task or variant.
- Repeat product invariants in every edit prompt.
- Prefer generating a clean visual base without dense text, then apply exact text with `scripts/render-text-overlay.py`.
- Validate file properties with `scripts/validate-image-file.py`.
- Inspect the result for product drift, incorrect text, invented claims, or unresolved diagnostic issues.
- Save accepted outputs under `outputs/tiktok-listing-optimizer/<sku-or-product-slug>/` in the active workspace.

If image generation is unavailable, output the complete image-task specification and production prompt. Do not claim an image was generated.

For transparent-background requests, keep `gpt-image-2`: generate or edit against a flat removable chroma-key background, then remove it locally. Because `gpt-image-2` does not support native `background=transparent`, report the limitation instead of switching to `gpt-image-1.5` or another model.

### 10. Produce the report

Follow [references/output-format.md](references/output-format.md). Preserve this traceability chain:

```text
evidence -> issue -> business impact -> recommendation -> copy/image deliverable -> validation
```

Use priorities:

- `P0`: compliance or factual blocker
- `P1`: high expected impact on conversion or click quality
- `P2`: useful experiment after P0 and P1 are resolved

## Tool failure behavior

- MCP failure: continue with public or user-provided evidence.
- Public-page failure: request screenshots or an export; do not guess page content.
- Missing original image: provide a reshoot brief; do not fabricate a sellable product image.
- Image drift: discard the version and restart from the original edit target.
- Wrong rendered text: keep a correct base image and redo only the deterministic text layer.
- Conflicting facts: show the conflict and require confirmation for publish-critical fields.

## Resource map

- `scripts/normalize-product-data.py`: normalize aliases, preserve provenance, and expose conflicts.
- `scripts/score-listing.py`: calculate the fixed 100-point readiness score.
- `scripts/render-text-overlay.py`: render exact Indonesian text over an accepted base image.
- `scripts/validate-image-file.py`: verify image format and technical properties.
- `references/indonesia-market-rules.md`: localization and compliance guardrails.
- `references/listing-scoring-rubric.md`: scoring checks and evidence rules.
- `references/indonesia-copywriting.md`: title, highlights, description, and keyword patterns.
- `references/ads-listing-alignment.md`: ad-to-listing comparison workflow.
- `references/mcp-data-mapping.md`: capability discovery and field groups.
- `references/image-optimization-workflow.md`: diagnosis-driven image tasks and validation.
- `references/output-format.md`: required deliverable structure.
- `references/sources.md`: source and reuse boundaries.
