# env-guard

Claude Code plugin: a PreToolUse hook that blocks access to the real `.env`
file (reading/editing/writing, shell reads, and scripts that read `.env` via
`open(".env")` / `load_dotenv()` etc.). Templates `.env.example` / `.env.*`
are allowed.

Layout:
- `env-guard/hooks/block-env.py` — hook logic
- `env-guard/hooks/hooks.json` — hook registration (must use the
  `{ "hooks": { ... } }` wrapper; loaded automatically from this standard path,
  so do NOT also reference it from `plugin.json`)
- `env-guard/.claude-plugin/plugin.json` — plugin manifest (holds `version`)
- `.claude-plugin/marketplace.json` — marketplace manifest

## Versioning (required)

Every substantive change MUST bump `version` in
`env-guard/.claude-plugin/plugin.json` following semver (`MAJOR.MINOR.PATCH`):

- **PATCH** — fixes with no user-visible behavior change (bug fix, narrowing or
  widening a match within the existing intent).
- **MINOR** — a new, backward-compatible capability or class of blocks.
- **MAJOR** — a breaking change (e.g. blocking something previously allowed, or
  a config-format change).

Substantive means any change to the hook logic, detection patterns, the
`matcher`, or the structure of `hooks.json`. Documentation-only edits (README,
comments, this file) do NOT change the version.

The marketplace is sourced from the GitHub repo, so `claude plugin update`
keys off committed changes — bumping the version makes updates visible and
deterministic. Bump the version in the same commit as the change itself.
