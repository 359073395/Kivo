# System And Restore

## Package Layout

- `skill/xuanpin`: portable Codex Skill.
- `project/tiktok-selection-system`: application source without dependencies or build output.
- `runtime-data/selection.sqlite`: current local business state, without integration token files.
- `business-data`: curated source-of-truth workbooks only.
- `knowledge`: selected product-selection knowledge and rules.
- `RESTORE_XUANPIN.ps1`: restores the project and Skill.
- `VERIFY_XUANPIN.ps1`: verifies allowlisted contents and checksums.

## Deliberately Excluded

- generated videos, images, subtitles and old reports;
- `node_modules`, build output, caches and logs;
- Git history and temporary imports/exports;
- API keys, OAuth tokens, encryption keys and `.env`;
- browser, LinkFox, TikTok, LLM and Feishu login state.

External services must be reauthorized after reinstall.

## Runtime Expectations

Local mode:

- Node.js 20 or newer;
- Corepack/pnpm;
- application root from `XUANPIN_HOME` or `D:\codex项目\apps\tiktok-selection-system`.

Production mode additionally uses Docker Compose, PostgreSQL, Redis, Caddy, a domain and environment secrets.

## Restore Notice

The restore script writes `%USERPROFILE%\.codex\xuanpin-restore-pending.json`. On the first later use of this Skill, report:

- restoration status and paths;
- available selection capabilities;
- external accounts that still need authorization;
- any failed install/test prerequisite.

Then run `scripts/acknowledge_restore.ps1`.

