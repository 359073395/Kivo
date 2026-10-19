# Required Output Format

Scale detail to the task, but preserve the section order and traceability.

## Contents

- [1. Data and confidence](#1-data-and-confidence)
- [2. Executive summary](#2-executive-summary)
- [3. Scorecard](#3-scorecard)
- [4. Findings and recommendations](#4-findings-and-recommendations)
- [5. Compliance review](#5-compliance-review)
- [6. Ready-to-use Bahasa Indonesia copy](#6-ready-to-use-bahasa-indonesia-copy)
- [7. Ad-to-listing alignment](#7-ad-to-listing-alignment)
- [8. Diagnosis-driven image tasks](#8-diagnosis-driven-image-tasks)
- [9. Generated image results](#9-generated-image-results)
- [10. Execution checklist](#10-execution-checklist)

## 1. Data and confidence

```text
Market: Indonesia
Mode: full optimization / audit only / image execution only
Sources used: MCP / public URL / screenshot / spreadsheet / user statement / original image
Missing data:
Conflicts:
Overall confidence: high / medium / low
```

Distinguish verified data from inference.

## 2. Executive summary

Explain in Chinese when the user speaks Chinese:

- the largest current conversion problem
- the three highest-priority changes
- whether the output is publish-ready, needs revision, or needs manual review

## 3. Scorecard

| Dimension | Before | Estimated after | Reason |
|---|---:|---:|---|
| Conversion readiness | | | |
| Search and title | | | |
| Image and click appeal | | | |
| Information and trust | | | |
| Variant and SKU clarity (price excluded) | | | |
| Ad-to-listing alignment | | | |
| Total | | | |

Also show data coverage, evidence coverage, compliance status, and publishing gate.

For Listing work, never include price, discount, voucher, promotion or subsidy as a diagnosis, recommendation, AI instruction or feedback criterion. Pricing and campaign work are separate user-triggered modes.

For a new product with no ad, display the ad-alignment row as `N/A`, show the applicable raw score and applicable maximum, and use the scorer's normalized 100-point total. Do not display the ad dimension as zero.

Fill `Estimated after` only for deliverables that were actually produced and validated. In audit-only mode or when an image/specification remains pending, use `not scored` or `—`; do not convert recommendations into a numeric projected score. Qualitative potential may be described separately.

## 4. Findings and recommendations

| Priority | Issue ID | Evidence | Funnel impact | Recommendation | Validation signal |
|---|---|---|---|---|---|

Use:

- `P0`: factual or compliance blocker
- `P1`: high expected impact
- `P2`: test after blockers and high-impact gaps are resolved

## 5. Compliance review

Separate `low`, `medium`, `high`, and `needs_review`. Do not call the result official approval.

## 6. Ready-to-use Bahasa Indonesia copy

### Recommended title

### Alternative titles

### Benefit highlights

### Product description

### Attribute and variant changes

### Keyword groups and evidence

### Excluded or risky wording

Include Chinese glosses only when they help the operator review accuracy.

This section must be safe to paste after human language review: no placeholders, bracketed fields, asterisks, or unverified claims. Put missing facts and optional post-verification lines in a separate subsection that is explicitly not publish-ready.

## 7. Ad-to-listing alignment

Show each ad/listing match, partial match, mismatch, and unknown. Resolve factual mismatches before visual continuity tests.

## 8. Diagnosis-driven image tasks

| Task | Linked issue | Source image | Objective | Allowed changes | Invariants | Acceptance criteria |
|---|---|---|---|---|---|---|

Do not list a task for an image that does not need modification.

## 9. Generated image results

For each executed task, show:

- final image or clickable file path
- prompt or edit specification
- technical validation
- product-preservation review
- exact-text review
- linked issue-resolution review
- accepted, revise, or discarded

When image tools are unavailable, label the section `Production prompts only` and do not imply completion.

## 10. Execution checklist

Group actions under P0, P1, and P2. End with a short human-review checklist. Never say the live listing was changed unless an explicitly authorized tool call actually changed it.
