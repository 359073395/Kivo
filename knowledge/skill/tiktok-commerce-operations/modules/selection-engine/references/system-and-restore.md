# System And Restore

## Current boundary

- The active entry is `tiktok-commerce-operations`; this file is an internal runbook reference, not a separate `xuanpin` Skill.
- The application source, database, imports, reports and runtime logs belong under the external path configured as `xuanpinHome`.
- Rules, reusable decisions, project summaries and final retrospectives belong in the knowledge vault.

## Deliberately Excluded

- generated videos, images, subtitles and old reports;
- `node_modules`, build output, caches and logs;
- Git history and temporary imports/exports;
- API keys, OAuth tokens, encryption keys and `.env`;
- browser, LinkFox, TikTok, LLM and Feishu login state.

External services must be reauthorized after reinstall.

## Runtime Expectations

Local mode dependencies and versions must be read from the current application itself. Resolve the application only from `machine-paths.local.json:xuanpinHome` or a path explicitly provided by the user; do not use a legacy fallback.

Production mode additionally uses Docker Compose, PostgreSQL, Redis, Caddy, a domain and environment secrets.

## Restore

Restoring the knowledge vault does not restore the external selection application, database or account sessions. Report the configured path, dependency checks and missing authorizations; never clear or acknowledge a legacy restore marker unless the user is explicitly restoring that old package.
