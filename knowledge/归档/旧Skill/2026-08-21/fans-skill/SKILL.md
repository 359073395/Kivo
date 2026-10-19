---
name: fans-skill
description: Create original Indonesian follower-growth short videos from viral references and static images, then build CapCut Desktop drafts with the user's 0703-style hook, subtitle, sticker, and music template. Use when the user says "fans Skill", asks for 涨粉视频, 爆款涨粉视频分析/仿写/批量生成, WhatsApp/TikTok health static-caption remakes, image-to-video batches, or CapCut draft automation instead of Jianying/剪映专业版.
---

# Fans Skill

## Goal

Turn a proven short-video reference into original follower-growth assets and editable CapCut drafts: viral-mechanic analysis, Indonesian hooks/scripts/captions, 9:16 static images, and batch draft creation.

Default to CapCut Desktop, not 剪映专业版, because the user's Indonesian subtitle workflow depends on CapCut.

## Portable Project Setup

Resolve the project root from the open workspace. If needed, use the
`FANS_PROJECT_ROOT` environment variable created by
`restore/RESTORE_FANS_PROJECT.ps1`.

Read `config/local_paths.json` before creating drafts or exports. Never
hard-code a Windows user name, CapCut version, or drive letter. Use:

- `capcut_templates/0703` as the source template.
- `templates/render_0703_exports.py` for burned-in exports.
- `default_work_root` for generated images, audio, and manifests.
- `default_export_root` for final videos.

Generated results must stay outside the portable backup project.

## Knowledge First

Before generating or editing, retrieve local memory:

```powershell
rg -n "fans|涨粉|0703|CapCut|静态图|字幕|健康|爆款|follow-growth" knowledge_base tiktok_copy_knowledge_base
```

Prioritize:

- `knowledge_base/04_short_video_content/health_static_caption_follow_growth_formula_20260703.md`
- `knowledge_base/06_tools_and_workflows/`
- `tiktok_copy_knowledge_base/README.md`
- `tiktok_copy_knowledge_base/viral_reference_database.md`
- `references/indonesia-common-ingredients.md`

Keep the work original: reuse mechanics and pacing, not exact wording, images, creator identity, or unlicensed assets.

## Non-Negotiable Rules

- The 0703 green quote sticker is one single circular icon aligned to the
  upper-left of the top hook text. Never use the full two-icon sticker frame.
- Food, plants, herbs, spices, drinks, and kitchen ingredients in scripts,
  hooks, captions, image prompts, and manifests must be common in Indonesia.
  Use `references/indonesia-common-ingredients.md` as the whitelist and
  locality check. If an ingredient is uncertain, replace it with a common
  Indonesian alternative before generating.
- Voice clarity has priority over background music. For burned-in exports,
  keep speech at `volume=1.0` and set background music to `volume=0.09` or
  lower. Never let the music cover the Indonesian voiceover.

## Workflow

1. Analyze the reference.
   - Extract duration, aspect ratio, first-frame visual, top hook, subtitle rhythm, audio/sticker style, CTA, and retention mechanics.
   - For health topics, soften claims with Indonesian wording such as `membantu`, `dikenal`, `bisa mendukung`, and avoid cure, guaranteed result, disease-treatment, or dosage promises.

2. Build the remake package.
   - Generate 10 original angles by default unless the user specifies another count.
   - For each angle, produce: slug, visual concept, top hook, 14 short Indonesian subtitle segments, CTA, caption text, and hashtags.
   - Run an ingredient-locality check: every food/plant ingredient must be a common Indonesian item, not a random imported wellness ingredient.
   - Save a machine-readable manifest under the configured
     `default_work_root`, such as
     `fans_<topic>_<yyyymmdd>/capcut_batch_manifest.json`.

3. Generate static images.
   - Create 9:16 images with no embedded text.
   - Leave clean top and lower-safe areas for CapCut text.
   - Use familiar Indonesian ingredients/products/scenes; avoid clutter that makes mobile reading hard.
   - Reject or revise image concepts that feature ingredients uncommon in Indonesian daily markets, kitchens, warung, jamu culture, or local home remedies.
   - Save images in the same batch folder with numbered slugs.

4. Create CapCut drafts.
   - If the user asks for the 0703 style, read `references/0703-capcut-style.md`.
   - Clone `capcut_templates/0703` into the configured `capcut_draft_root`,
     copy each image into the draft resources, replace visual media, rewrite
     the top hook, add a generated subtitle track, preserve stickers and
     music, and update root meta with a timestamped backup.
   - Keep background music at least 50% lower than the previous render setting; default renderer value is `volume=0.09`.
   - Use a JSON parser for `draft_content.json`, `draft_meta_info.json`, `key_value.json`, and `root_meta_info.json`; do not edit draft JSON by string replacement.

5. Verify before handoff.
   - Confirm each draft folder exists under the configured
     `capcut_draft_root`.
   - Confirm root meta contains every new draft.
   - Confirm each draft has expected media, text, sticker, and audio tracks.
   - Tell the user to reopen or refresh CapCut if the drafts are not visible.

## Reference Selection

- Read `references/health-static-caption-formula.md` for the WhatsApp 2026-07-03 health/follow-growth formula, caption beats, and compliant Indonesian copy pattern.
- Read `references/0703-capcut-style.md` when matching the user's `0703` CapCut draft, top hook, subtitle style, sticker layout, music, or batch draft automation.
- Read `references/indonesia-common-ingredients.md` before generating health/natural-remedy food or plant topics.

## Output Contract

For batch work, return:

- Batch folder path.
- Image paths.
- Manifest path.
- CapCut draft names and draft root path.
- Verification summary and any manual CapCut refresh note.

Use concise Chinese status updates for the user while working.
