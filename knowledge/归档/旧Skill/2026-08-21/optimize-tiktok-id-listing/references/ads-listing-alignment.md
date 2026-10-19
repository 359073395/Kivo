# Ad-to-Listing Alignment

Use this workflow when an ad creative, video script, caption, product card, or promotion sends traffic to the listing.

## Build the comparison matrix

Compare the ad and listing for:

| Area | Ad evidence | Listing evidence | Result |
|---|---|---|---|
| Product identity | Product, model, visible packaging | Title, images, attributes | match / partial / mismatch / unknown |
| Variant scope | Color, size, bundle, quantity | Selected and available variants | match / partial / mismatch / unknown |
| Price | Displayed price and qualifiers | Listing and selected-variant price | match / partial / mismatch / unknown |
| Promotion | Discount, voucher, shipping, deadline | Current listing terms | match / partial / mismatch / unknown |
| Gift and contents | Gift, accessories, bundle | Package contents | match / partial / mismatch / unknown |
| Claim | Benefit, performance, result | Listing proof and product evidence | match / partial / mismatch / unknown |
| Creative hook | First-frame promise | Listing first-screen message | match / partial / mismatch / unknown |

## Severity

- `P0`: different product, unsupported effect, false price, unavailable gift, or publish-blocking claim.
- `P1`: the ad promise is real but the listing does not surface the proof or message quickly enough.
- `P2`: tone, hierarchy, or visual continuity can be tested after factual alignment is fixed.

## Remediation order

1. Correct factual mismatch.
2. Confirm the offer and variant scope.
3. Bring verified ad proof into the listing.
4. Align first-screen visual hierarchy and wording.
5. Create a test only after one coherent baseline exists.

Never alter the listing to preserve an inaccurate ad promise. Correct the ad or remove the unsupported claim.

## Output

For every mismatch, report:

```text
alignment_issue_id
ad evidence
listing evidence
buyer expectation created
risk or conversion impact
recommended correction
asset or field to change
validation method
```

