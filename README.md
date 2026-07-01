# env-guard — Claude Code plugin

A tiny Claude Code plugin that **blocks all access to the real `.env` file** — reading, editing,
writing, or reading it through shell commands (`cat`, `grep`, `head`, `sed`, `vim`, …). Templates
like `.env.example`, `.env.local`, and `.env.*` stay allowed.

Why: `.env` holds live secrets. New or changed variables belong in `.env.example`, with a note
telling the human which parameter to copy into their local `.env`.

Cross-platform: the guard is pure Python 3 (no dependencies) and the hook uses the plugin's
`${CLAUDE_PLUGIN_ROOT}` path via the exec (`args`) form, so it works under bash **and** PowerShell
on Windows, macOS, and Linux.

## Install (for students)

In Claude Code, run:

```
/plugin marketplace add OleksandrCEO/claude-env-guard
/plugin install env-guard@env-guard-marketplace
```

Then restart Claude Code (or open `/plugin` once) so the hook activates. Done — no files to copy.

## Requirements

- **Python 3 on `PATH`** (the hook runs `python3`).
- **Windows:** if `python3` is not recognized, install Python from python.org (which provides the
  `py` launcher and usually a working `python3`), or from the Microsoft Store (which creates
  `python3.exe`). If you must use `python` instead, edit `env-guard/hooks/hooks.json` and change
  `"command": "python3"` to `"command": "python"`.

## Verify

Ask Claude to read `.env` — it should be denied with a message pointing you to `.env.example`.
Reading `.env.example` still works.

## What is / isn't blocked

| Action | Result |
|---|---|
| Read/Edit/Write a file named exactly `.env` | ❌ blocked |
| Shell command referencing a `.env` path | ❌ blocked |
| `.env.example`, `.env.local`, `.env.<anything>` | ✅ allowed |
| Everything else | ✅ allowed |

The guard **fails open** on malformed hook input, so it can never break your tool pipeline.

## Repo layout

```
.claude-plugin/marketplace.json   # marketplace manifest (lists the plugin)
env-guard/
├── .claude-plugin/plugin.json    # plugin manifest
└── hooks/
    ├── hooks.json                # registers the PreToolUse hook
    └── block-env.py              # the guard logic
```

## License

MIT
