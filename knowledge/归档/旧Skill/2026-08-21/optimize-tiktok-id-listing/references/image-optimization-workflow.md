# Diagnosis-Driven Image Optimization

Do not run image generation as an independent creative exercise. Every image task must consume a specific diagnostic recommendation and return to that issue for validation.

## Contents

- [Decision flow](#decision-flow)
- [Create an image task only when](#create-an-image-task-only-when)
- [Task specification](#task-specification)
- [Prompt construction](#prompt-construction)
- [Product-preservation rules](#product-preservation-rules)
- [Text strategy](#text-strategy)
- [Scene and prop checks](#scene-and-prop-checks)
- [Output path and versioning](#output-path-and-versioning)
- [Model and transparency policy](#model-and-transparency-policy)
- [Validation record](#validation-record)

## Decision flow

```text
listing evidence
-> diagnosed issue
-> prioritized recommendation
-> image task specification
-> image edit or generation
-> technical validation
-> product-invariant review
-> issue-resolution review
-> accept, revise, or discard
```

## Create an image task only when

- the issue affects click quality, comprehension, trust, variant selection, or conversion
- a visual change is the appropriate remedy
- the required product facts and source images exist
- the intended claim or scene is supportable
- acceptance criteria can be stated before generation

Keep an existing image unchanged when it already satisfies the recommendation.

## Task specification

```json
{
  "task_id": "IMG-P1-01",
  "issue_id": "CLICK-01",
  "funnel_stage": "click",
  "objective": "Make the real product recognizable at mobile thumbnail size",
  "input_images": [
    {"path": "source/main.jpg", "role": "edit_target"}
  ],
  "allowed_changes": ["background", "crop", "lighting", "product scale within frame"],
  "invariants": ["product shape", "packaging", "color", "logo", "labels", "accessory count"],
  "exact_text": [],
  "prohibited": ["new accessories", "certification badge", "discount text"],
  "acceptance_criteria": [
    "product occupies the intended frame area",
    "packaging and logo match the source",
    "no object appears to be included unless it is in package contents"
  ],
  "output_filename": "SKU-main-v2.png"
}
```

## Prompt construction

Invoke the available `imagegen` skill for raster work. Use its bundled CLI and pass `--model gpt-image-2` explicitly for all generation and editing. Do not use another model or an unconfirmed built-in model path. Label every input image role. For edits, repeat invariants in each prompt.

Live CLI calls require a locally configured `OPENAI_API_KEY`. Never request that the user paste the key into chat. Do not pass `--input-fidelity` with `gpt-image-2`.

Use this prompt structure:

```text
Use case: precise-object-edit or compositing
Asset type: TikTok Shop Indonesia product listing image
Primary request: <single diagnostic objective>
Input images: Image 1 is the edit target; other images have explicit supporting roles
Scene/backdrop: <only if supported by the use case>
Composition/framing: <mobile-first target>
Text (verbatim): "<short exact Indonesian text>"
Constraints: change only <allowed changes>; preserve <invariants>
Avoid: <prohibited claims, props, badges, gifts, or visual implications>
Acceptance criteria: <task criteria>
```

## Product-preservation rules

Preserve aggressively:

- shape, proportions, structure, model, and visible mechanisms
- packaging, color, brand, logo, labels, and printed specifications
- included items and accessory count
- material appearance when it affects the buyer's expectation

Discard the result when the model changes any invariant. Do not repair a drifted product by continuing to edit the wrong version; restart from the original edit target.

## Text strategy

- Keep image copy short and factual.
- Prefer a clean generated base without dense model-rendered text.
- Place exact Indonesian wording with `scripts/render-text-overlay.py` after the base image passes product review.
- Do not use badges, seals, review stars, percentages, or urgency text without verified source evidence.
- Re-render only the text layer when wording is wrong.

Example overlay spec:

```json
{
  "overlays": [
    {
      "text": "Ringan dan Mudah Dibawa",
      "box": [0.08, 0.67, 0.84, 0.22],
      "font_size": 64,
      "min_font_size": 28,
      "fill": "#FFFFFFFF",
      "background": "#00000099",
      "align": "center",
      "valign": "middle",
      "padding": 20,
      "radius": 16
    }
  ]
}
```

## Scene and prop checks

- A lifestyle scene must show a verified use case.
- Props must not look like included accessories or gifts.
- Human models must not imply an unsupported demographic, safety rating, medical result, or product scale.
- Comparison images require comparable verified facts; never invent a competitor comparison.
- Before/after images require authentic, permitted evidence and heightened review. Otherwise do not create them.

## Output path and versioning

Save accepted workspace assets under:

```text
outputs/tiktok-listing-optimizer/<sku-or-product-slug>/
```

Use descriptive versioned names such as:

```text
SKU-main-v2.png
SKU-material-detail-v1.png
SKU-size-guide-v1.png
```

Never overwrite the source image.

## Model and transparency policy

- Required model: `gpt-image-2`.
- Run the bundled imagegen CLI; do not create a one-off SDK script.
- Use `quality=low` for optional drafts and `quality=medium` or `high` for selected final assets.
- Do not use `background=transparent`; `gpt-image-2` does not support native transparent output.
- When transparency is needed, request a perfectly flat chroma-key background from `gpt-image-2`, remove it locally, and validate the alpha result.
- If the subject is unsuitable for reliable chroma-key removal, report that true native transparency is unavailable under the required-model policy. Do not silently switch to `gpt-image-1.5`.

Use commands shaped like:

```bash
python "$IMAGE_GEN" edit \
  --model gpt-image-2 \
  --image source.png \
  --prompt-file image-task-prompt.txt \
  --quality high \
  --out outputs/tiktok-listing-optimizer/SKU/SKU-main-v2.png
```

## Validation record

For each image, record:

```text
task ID and linked issue ID
source image
final file path
final prompt
technical validation result
product-invariant result
Indonesian text result
claim and offer result
issue-resolution result
decision: accepted / revise / discarded
```

Technical validation does not replace visual review. Use `scripts/validate-image-file.py` for file properties, then visually inspect all invariants and acceptance criteria.
