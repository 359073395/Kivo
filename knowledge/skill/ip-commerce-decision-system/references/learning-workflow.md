# Continuing Learning Workflow

Use this when the user provides videos, audio, documents, spreadsheets, PDFs, screenshots, folders or course materials and asks to learn, distill or update the knowledge base.

## Storage rule

- Original video/audio/PDF binaries, frames, temporary transcription/OCR caches and other large binaries stay in the external local work directory.
- Final cleaned Markdown transcripts/manuscripts, distilled knowledge, source indexes, method cards, project summaries and final retrospectives stay in the knowledge vault.
- Do not copy passwords, cookies, tokens, API keys or private login state into either a method card or project handoff.

## Process

1. Inventory all files and record counts by media, document, sheet, image, transcript and unreadable item.
2. Process the complete source. Sampling is only a preview and must stay `partial`, even when the user accepts a preview.
3. Extract claims, concepts, formulas, workflows, examples, failure cases, prerequisites, checks and stop conditions.
4. Separate source facts from interpretation and conflicts.
5. Classify reusable learning as `personal_ip`, `commerce_video` or both.
6. Convert descriptive knowledge into decision units using `decision-protocol.md`.
7. Compare against existing method cards; merge duplicates, preserve disagreements and avoid rewriting large handbooks unnecessarily.
8. Create a candidate rule before changing an active rule. Record scope, evidence, counterexamples and validation plan.
9. Update the knowledge log with sources, changed files, important judgments, unreadable items and next steps.

## Source handling

- Fully transcribe video/audio into timestamped Markdown; add meaningful screen text and visual-only information, and report any partial coverage.
- Convert every page of DOCX/PPTX/PDF into readable Markdown; use full-page OCR for scans and preserve page/slide anchors, tables and notes.
- Preserve tables that are templates, scripts, prompts, checklists or metrics.
- OCR image-heavy material when needed.
- Do not treat course branding or filenames as the final knowledge classification.

## Output for every learning batch

```text
Source scope and completeness
New reusable knowledge
Applicable situation and non-applicable scope
Execution and decision gates
Checks and stop conditions
Conflicts with existing rules
Candidate updates requiring review
Files updated
Unreadable or missing evidence
```

After real-world feedback, run `input -> digest -> output -> feedback -> log` and upgrade rules only after validation and user approval.
