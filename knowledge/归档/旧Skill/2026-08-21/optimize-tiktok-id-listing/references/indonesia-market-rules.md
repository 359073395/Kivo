# Indonesia Market and Compliance Guardrails

Use these as conservative operational guardrails for TikTok Shop Indonesia listing work. Platform rules, category restrictions, field limits, and enforcement practices can change. Prefer current official TikTok documentation, Seller Center notices, and authorized MCP data whenever available.

Do not describe this review as legal advice or official platform approval.

## Evidence hierarchy

Use this order for publish-critical facts:

1. Current Seller Center or authorized TikTok MCP data.
2. Current official TikTok policy or category documentation.
3. Product packaging, manufacturer documentation, certificates, and user-provided source files.
4. Public product page and ad creative.
5. User statements that have not yet been independently verified.
6. Inference. Never publish an inference as a fact.

When sources conflict, expose the conflict. Do not silently choose the most persuasive value.

## Bahasa Indonesia localization

- Write for natural Indonesian reading patterns, not word-for-word translation from Chinese or English.
- Lead with the product type and concrete buyer benefit when evidence supports it.
- Prefer common buyer vocabulary over technical jargon; retain necessary model and specification terms.
- Use `Rp` and Indonesian number formatting when presenting IDR prices, while preserving the exact source value.
- Keep units consistent with product evidence. Do not convert dimensions or capacity without checking the arithmetic.
- Explain unfamiliar imported terms briefly rather than stuffing synonyms.
- Keep image text short, legible, factual, and consistent with the listing.
- Avoid fake slang, forced trend language, or excessive emoji when it reduces clarity or trust.

## Factual claim checks

Require evidence before using:

- medical, therapeutic, health, weight-loss, skin, hair, or body-effect claims
- safety, child-safe, food-safe, waterproof, fireproof, antibacterial, hypoallergenic, or protective claims
- laboratory results, percentages, duration, capacity, speed, power, compatibility, or performance claims
- halal, BPOM, SNI, organic, eco, cruelty-free, imported, original, official, or warranty claims
- best seller, number one, guaranteed, permanent, instant, risk-free, or zero-side-effect claims
- customer counts, ratings, testimonials, before/after results, and endorsements

If the evidence is incomplete, remove the claim or classify it as `needs_review`.

## Price, promotion, and package checks

- Match listing, ad, image, selected variant, voucher, bundle, and checkout price context.
- Do not create an original price, discount percentage, urgency deadline, stock scarcity, gift, or free-shipping promise without a current source.
- State which variant a displayed price applies to when variants differ materially.
- List package contents exactly. Do not add decorative props to a generated image if they could be mistaken for included items.
- Distinguish a bundle from a single unit and show quantity clearly.

## Variant and attribute checks

- Use consistent names for colors, sizes, models, flavors, capacities, and bundles across title, attributes, images, ads, and SKU selectors.
- Do not merge two materially different variants into one promise.
- Surface compatibility limits and required accessories when buyers need them to avoid a wrong purchase.
- Treat missing attributes as a conversion and return-risk issue, not merely an SEO issue.

## Visual guardrails

- Keep the actual product dominant and recognizable on mobile.
- Preserve product shape, packaging, color, logo, labels, model, specifications, and accessory count.
- Do not generate certifications, seals, star ratings, testimonials, platform badges, or review screenshots.
- Do not generate unverified before/after images.
- Avoid visualizing an effect that the product evidence cannot support.
- Ensure props, hands, models, rooms, and environments do not imply an unsupported scale, use case, demographic, or included item.
- Keep dense paragraphs out of images. Use deterministic overlays for exact short text.

## Categories requiring heightened review

Use `needs_review` or `high` when source evidence is insufficient for regulated or high-risk categories, including:

- supplements, food, beverages, and ingestible products
- cosmetics, skincare, haircare, and personal-care effect claims
- medical, wellness, posture, pain, sleep, or body-shaping products
- baby, child, safety, protective, and electrical products
- batteries, chargers, appliances, chemicals, pesticides, and hazardous materials
- products using trademarks, character IP, celebrity identity, or comparative competitor claims

Do not invent category-specific legal requirements. Ask for current official documentation when a conclusion depends on it.

## Risk levels

- `low`: wording or presentation risk; warn and continue.
- `medium`: revise before treating the deliverable as publish-ready.
- `high`: stop generating the affected claim or image.
- `needs_review`: evidence or current policy is insufficient for an automated conclusion.

## Minimum publish-ready evidence

Before marking content publish-ready, confirm:

- product identity, model, and variant
- price and promotion context
- key specifications and package contents
- source for every non-obvious claim
- listing and ad consistency
- image preservation of the real product
- manual review of generated text and images

