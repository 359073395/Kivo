# 0703 CapCut Style Reference

Use this reference when the user asks to copy the `0703` draft's top hook, subtitle style, stickers, music, or batch CapCut draft structure.

## Local Paths

Read these machine-specific values from `config/local_paths.json`:

- `capcut_user_data`
- `capcut_root_meta`
- `capcut_draft_root`
- `capcut_template`

The portable source template is always
`<project_root>/capcut_templates/0703`. Never hard-code a Windows user name,
CapCut version, or drive letter.

Always back up the configured `capcut_root_meta` before editing:

```text
root_meta_info.backup_YYYYMMDD_HHMMSS.json
```

## Template Findings

The `0703` draft has:

- One editable top text material:
  - `BADAN SERING PEGAL?\nCOBA MINUM HANGAT INI`
- No separate editable subtitle track; simulate subtitles by adding a text track.
- Two sticker tracks:
  - Green quote sticker: `Comperehension focus`
  - Red oval/arrow sticker: `Highlight EN Red Line Oval Marker Arrow`
- Two audio tracks:
  - `speechma_audio_Brian_Indonesian_at_5_19_47_PM_on_July_3rd_2026.mp3`
  - `Mozart Andante for Piano`

## Audio Mix Rule

Voice clarity is mandatory. In burned-in exports, the Indonesian voiceover must
stay clearly louder than the background music:

```text
speech volume: 1.0
background music volume: 0.09 or lower
```

Do not use the older `0.18` music-volume setting; it makes the voiceover too
hard to hear.

## Top Hook Style

Match these settings when rewriting the top hook:

```json
{
  "font_size": 15,
  "font_path": "<project_root>/capcut_assets/fonts/capcut_en.ttf",
  "text_color": "#000000",
  "background_color": "#ffffff",
  "background_style": 2,
  "background_round_radius": 0.4000000059604645,
  "background_width": 0.2800000011920929,
  "background_height": 0.2800000011920929,
  "border_color": "#ffffff",
  "border_width": 0.08,
  "shadow_enabled": false,
  "transform": {
    "x": 0.05932203389830515,
    "y": 0.4964200477326969
  },
  "clip_scale": {
    "x": 0.6861332929088458,
    "y": 0.6861332929088458
  }
}
```

Top hook copy pattern:

```text
<SHORT PAIN QUESTION?>
COBA <SIMPLE ACTION/DRINK/FOOD>
```

Use uppercase Indonesian, 2 lines, short enough to fit the existing box.

## Green Quote Sticker

This is a locked rule. The title decoration must be one small green circular
quote icon aligned to the upper-left of the top hook text. Do not render the
full `SequenceMap.png` frame: the visible CapCut frame contains two vertically
stacked quote icons, which creates a duplicated sticker if used directly.

Never place the quote icon as a free-floating canvas decoration. Its position
must follow the top hook text block.

For burned-in exports, use the already cropped portable icon and place it
relative to the title, not relative to the video canvas. The current 1080x1920
renderer uses:

```text
source: <project_root>/capcut_assets/stickers/0703_green_quote_single.png
source size: cropped upper 110x110 icon from the original sprite frame
render size: 96x96
overlay: x=214, y=334
```

## Subtitle Track

Because `0703` has no editable subtitle track, add subtitles as a new text track using the same material style family:

- Lower-safe placement: `y = -0.625`
- Scale: `0.64`
- Black text on white rounded background.
- Use 14 segments for the default 43.666s remake.
- Keep each subtitle short; split long Indonesian clauses.

## Draft Generation Checklist

For each generated draft:

1. Clone `<project_root>/capcut_templates/0703` to
   `<capcut_draft_root>/<draft_name>`.
2. Copy the generated image into the draft resources/local assets.
3. Replace visual media references with the generated image.
4. Rewrite the existing top text material.
5. Add or replace the generated subtitle text track.
6. Preserve sticker and audio tracks.
7. Set draft duration to `43_666_666` microseconds unless matching a different reference.
8. Update `draft_meta_info.json`, `key_value.json`, and root meta.
9. Parse the resulting JSON to verify it is valid.

Recommended draft naming:

```text
fans_<nn>_<slug>_0703style
```

If CapCut does not show the drafts, close and reopen CapCut after confirming root meta contains the new draft entries.
