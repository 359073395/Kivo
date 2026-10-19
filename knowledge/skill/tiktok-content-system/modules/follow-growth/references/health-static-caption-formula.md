# Health Static-Caption Follow-Growth Formula

Use this reference when the user asks to remake the WhatsApp 2026-07-03 viral follower-growth video or asks for health/natural-remedy static caption videos.

## Source Pattern

- Source file:
  `<project_root>/reference_media/WhatsApp Video 2026-07-03 at 16.11.31.mp4`
- Format: vertical 9:16, 576x1024, about 50.7 seconds.
- Core visual: almost-static close-up of familiar kitchen ingredients.
- Retention driver: fast Indonesian subtitles and a fixed top hook, not scene changes.
- CTA: follow for more health knowledge.

## Reusable Structure

1. Symptom-pain hook.
2. Familiar overlooked kitchen ingredients.
3. Benefit stack with soft claims.
4. Delayed simple usage method.
5. Broad wellness payoff.
6. Follow CTA tied to more knowledge.

## Ingredient Locality Rule

For Indonesian remakes, every food, plant, herb, spice, drink, or kitchen
ingredient must be common in Indonesia. Prefer ingredients people recognize
from pasar, warung, daily kitchens, jamu culture, and local home remedies.

Before finalizing a script or image prompt, check
`references/indonesia-common-ingredients.md`. Replace imported or niche wellness
items with familiar Indonesian alternatives.

## Default 14-Beat Caption Timeline

For a 43.666s CapCut remake, use these starts and durations unless the template requires changes:

| Beat | Start | Duration | Purpose |
|---|---:|---:|---|
| 1 | 0.5 | 2.4 | Pain question |
| 2 | 2.9 | 2.6 | Audience confirmation |
| 3 | 5.5 | 2.8 | Kitchen ingredient reveal |
| 4 | 8.3 | 2.8 | Ingredient 1 familiar benefit |
| 5 | 11.1 | 2.8 | Ingredient 2 familiar benefit |
| 6 | 13.9 | 3.2 | Pairing curiosity |
| 7 | 17.1 | 3.2 | Body comfort / daily wellness |
| 8 | 20.3 | 3.0 | Digestion / warmth / lightness |
| 9 | 23.3 | 3.1 | Antioxidant or traditional-use note |
| 10 | 26.4 | 3.1 | Simple preparation tease |
| 11 | 29.5 | 3.2 | Usage method |
| 12 | 32.7 | 4.0 | Safety/consistency note |
| 13 | 36.7 | 4.0 | Payoff |
| 14 | 40.7 | 2.9 | Follow CTA |

## Indonesian Copy Guardrails

Use:

- `bisa membantu`
- `dikenal secara tradisional`
- `mendukung`
- `lebih nyaman`
- `hasil tiap orang bisa berbeda`
- `bukan pengganti nasihat dokter`

Avoid:

- `menyembuhkan`
- `mengobati`
- `pasti turun`
- `hilang total`
- fixed medical dosage claims
- direct treatment claims for hypertension, cholesterol, gout, heart disease, inflammation, or diabetes

## Image Prompt Rules

- Generate realistic or clean editorial 9:16 images.
- No text inside the image.
- Keep subject readable in the first second.
- Leave clean space near the top for the hook and lower area for subtitles.
- Use ingredients/products that match the script; do not reuse the original garlic-coriander composition unless the user specifically requests that case.
- Use Indonesian-common ingredients only. Avoid imported/niche wellness props
  unless the user explicitly asks for that exact ingredient and accepts the
  locality tradeoff.

## Portable Output Rule

Historical batch images, manifests, drafts, and exports are intentionally not
included in the portable project. Create each new batch under the configured
`default_work_root` and write final videos under `default_export_root`.
