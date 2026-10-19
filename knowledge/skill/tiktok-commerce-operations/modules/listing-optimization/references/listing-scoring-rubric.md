# Listing Scoring Rubric

Use the exact check IDs below with `scripts/score-listing.py`.

## Contents

- [Values](#values)
- [Conversion readiness — 30 points](#conversion-readiness--30-points)
- [Search and title — 20 points](#search-and-title--20-points)
- [Image and click appeal — 15 points](#image-and-click-appeal--15-points)
- [Information and trust — 15 points](#information-and-trust--15-points)
- [Price, promotion, and SKU — 10 points](#price-promotion-and-sku--10-points)
- [Ad-to-listing alignment — 10 points](#ad-to-listing-alignment--10-points)
- [Compliance status](#compliance-status)

## Values

- `1`: fully satisfied with evidence
- `0.5`: partly satisfied, inconsistent, weak, or incomplete
- `0`: clearly absent, incorrect, misleading, or unusable
- `null`: unavailable or cannot be assessed from current evidence

Every non-null value should include at least one evidence string. Unknown checks receive no readiness points and reduce data coverage. Never guess a passing value to improve the score.

Score only the artifact and evidence that exist at the time of assessment. A planned rewrite, proposed image, unverified claim, reshoot brief, or future MCP field cannot receive points. Create an after-assessment only after the corresponding deliverables exist and have passed factual, compliance, and image-preservation review.

Assessment JSON shape:

```json
{
  "checks": {
    "conversion.primary_value_clear": {
      "value": 1,
      "evidence": ["Title and first image state the product and primary use"]
    }
  },
  "not_applicable_dimensions": [],
  "compliance": {
    "status": "pass",
    "issues": []
  },
  "notes": []
}
```

For a new product that genuinely has no ad or campaign, use `"not_applicable_dimensions": ["ad_alignment"]`. The scoring script excludes that dimension and normalizes the remaining applicable maximum to 100. Do not use N/A when an ad exists but evidence is missing; use `null` checks instead.

## Conversion readiness — 30 points

| Check ID | Full | Partial | Fail |
|---|---|---|---|
| `conversion.primary_value_clear` | Product and primary value are immediately clear | Value requires interpretation | Product or value is unclear |
| `conversion.benefit_supported` | Main benefits follow verified features or proof | Some benefits lack support | Benefits are absent or misleading |
| `conversion.use_case_clear` | Key use cases and audience are clear and factual | Only one vague use case | Buyer cannot tell when or why to use it |
| `conversion.key_specs_visible` | Purchase-critical specs are easy to find | Specs exist but are buried or incomplete | Critical specs are missing or contradictory |
| `conversion.package_contents_clear` | Included items and quantity are explicit | Mostly clear with minor ambiguity | Contents are missing or misleading |
| `conversion.variant_choice_clear` | Differences between variants are obvious | Some options are confusing | Variants can easily cause a wrong purchase |
| `conversion.how_to_use_clear` | Required setup or usage is clear | Basic guidance exists | Necessary usage information is absent |
| `conversion.objections_addressed` | Major buyer questions and limits are answered | Some objections remain | Material objections are ignored |
| `conversion.purchase_path_clear` | Offer, variant, and purchase action are coherent | Minor purchase friction remains | Buyer cannot understand what to select or receive |
| `conversion.mobile_scan_friendly` | First screen and copy are easy to scan on mobile | Some dense or weak hierarchy | Key information is unreadable or buried |

## Search and title — 20 points

| Check ID | Full | Partial | Fail |
|---|---|---|---|
| `search.product_type_present` | Clear product-type term is present | Product type is indirect | Product type is absent |
| `search.primary_keyword_early` | Evidence-backed primary term appears early | Term appears late | Relevant primary term is absent |
| `search.secondary_keywords_natural` | Useful secondary terms are integrated naturally | Coverage is thin or awkward | Terms are absent or stuffed |
| `search.title_matches_product` | Title exactly matches real product and variant scope | Minor ambiguity | Title is inaccurate or misleading |
| `search.category_specificity` | Most specific verified category is used | Category may be too broad | Category is wrong or unknown |
| `search.attributes_complete` | Search and purchase-critical attributes are complete | Several useful attributes are missing | Attributes are largely absent or wrong |
| `search.variant_terms_consistent` | Variant names are consistent everywhere | Minor naming inconsistency | Variant naming conflicts materially |
| `search.no_keyword_stuffing` | Title reads naturally without repetition | Slight repetition or clutter | Obvious stuffing harms clarity |
| `search.indonesian_search_language` | Terms reflect natural Indonesian buyer language | Some untranslated or unnatural terms | Copy is not localized for Indonesian search |
| `search.keyword_evidence_available` | Keywords come from live data, buyer language, or verified comparable evidence | Evidence is limited | Search-volume or trend claims are invented |

## Image and click appeal — 15 points

| Check ID | Full | Partial | Fail |
|---|---|---|---|
| `click.product_dominant` | Product is large, clear, and recognizable | Product is visible but weak | Product is obscured or too small |
| `click.background_clear` | Background supports fast recognition | Some distraction remains | Background competes with or hides product |
| `click.mobile_legible` | Important visual and text details survive mobile size | Some details are too small | Key content is unreadable on mobile |
| `click.visual_hierarchy` | One clear focal point and reading order | Hierarchy is inconsistent | Image is cluttered or directionless |
| `click.key_differentiator_visible` | Verified differentiator is visually clear | Differentiator is weak | No meaningful or factual differentiator is visible |

## Information and trust — 15 points

| Check ID | Full | Partial | Fail |
|---|---|---|---|
| `trust.brand_identity_consistent` | Brand, logo, product, and packaging match across assets | Minor variation | Identity conflicts or appears fabricated |
| `trust.factual_claims` | All material claims are supported | Some claims need review | Claims are false, invented, or high risk |
| `trust.specs_consistent` | Specifications agree across all sources | Minor gaps | Material specification conflicts exist |
| `trust.package_contents_consistent` | Visuals and copy show the same included items | Small ambiguity | Props or copy imply wrong contents |
| `trust.proof_or_limitations_clear` | Proof and material limits are visible where needed | Some limits are buried | Proof is absent or limits are hidden |

## Price, promotion, and SKU — 10 points

| Check ID | Full | Partial | Fail |
|---|---|---|---|
| `price_sku.price_visible_consistent` | Price context matches listing, ad, image, and variant | Minor timing or display ambiguity | Conflicting or misleading price |
| `price_sku.promotion_truthful` | Discount, voucher, urgency, and gift are current and sourced | Some terms need clarification | Promotion is invented or contradictory |
| `price_sku.variants_clear` | Variant price and contents are clearly differentiated | Some options remain confusing | Variant structure is misleading |
| `price_sku.bundle_value_clear` | Bundle quantity and value are explicit | Bundle is partly explained | Buyer cannot tell unit versus bundle |
| `price_sku.value_context_clear` | Price is understandable for the selected quantity, specification, or bundle | Value context is incomplete | Buyer cannot tell what the displayed price buys |

## Ad-to-listing alignment — 10 points

| Check ID | Full | Partial | Fail |
|---|---|---|---|
| `ad_alignment.product_identity_match` | Same product, model, and variant scope | Minor creative variation | Ad lands on a materially different item |
| `ad_alignment.price_promo_match` | Price, discount, voucher, and deadline match | Minor context gap | Offer conflicts materially |
| `ad_alignment.claim_match` | Ad claims are supported on the listing | Some proof is weak | Ad promise is absent, contradicted, or unsupported |
| `ad_alignment.variant_gift_match` | Variant, quantity, gift, and package match | Minor ambiguity | Ad implies unavailable contents or variant |
| `ad_alignment.creative_landing_message_match` | Creative hook and listing first screen continue the same message | Connection is weak | Landing experience breaks the ad promise |

## Compliance status

Use one value:

- `pass`
- `low`
- `medium`
- `high`
- `needs_review`

The score script converts these to `clear`, `warning`, `revise_before_publish`, `blocked`, or `manual_review_required` publishing gates.
