# MagWer ENV Guard — Claude Code plugin

![version](https://img.shields.io/github/v/tag/OleksandrCEO/claude-env-guard?label=version&sort=semver)
![license](https://img.shields.io/badge/license-MIT-green)
![python](https://img.shields.io/badge/python-3.x-blue)
![platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey)

A small, dependency-free Claude Code plugin that **blocks all access to the real `.env` file** —
whether Claude tries to read, edit, or write it directly, reach it through a shell command, or
run a script that loads it. Templates like `.env.example`, `.env.local`, and `.env.*` stay allowed.

**Why:** `.env` holds live secrets. New or changed variables belong in `.env.example`, with a note
telling the human which parameter to copy into their local `.env`.

## Features

- **Direct file access** — `Read` / `Edit` / `Write` on a file named exactly `.env` is denied.
- **Shell reads** — Bash commands that touch `.env` (`cat`, `grep`, `head`, `sed`, `source`,
  `export $(cat .env)`, …) are denied.
- **Scripts that read `.env`** — writing or editing a script whose contents open `.env`
  (`open(".env")`, `load_dotenv()`, `dotenv.config()`, `godotenv.Load`, …) is denied, and Bash
  commands that *run* such a script (`python app.py`, `node app.js`, `./run.sh`) are inspected on
  disk and denied too.
- **Templates allowed** — `.env.example`, `.env.local`, `.env.<anything>` always pass.
- **No false positives on env vars** — reading process environment (`os.getenv`, `process.env`)
  is *not* blocked; only reading the `.env` file is.
- **Fails open** — on malformed hook input it never blocks, so it can't break your tool pipeline.

## What is / isn't blocked

| Action | Result |
|---|---|
| Read / Edit / Write a file named exactly `.env` | ❌ blocked |
| Shell command referencing a `.env` path (`cat`, `source`, …) | ❌ blocked |
| Writing a script that reads `.env` (`open(".env")`, `load_dotenv()`) | ❌ blocked |
| Running a script file that reads `.env` (`python app.py`, `./run.sh`) | ❌ blocked |
| `.env.example`, `.env.local`, `.env.<anything>` | ✅ allowed |
| Reading process env vars (`os.getenv`, `process.env`) | ✅ allowed |
| Everything else | ✅ allowed |

## Install

In Claude Code, run:

```
/plugin marketplace add OleksandrCEO/claude-env-guard
/plugin install env-guard@env-guard-marketplace
```

Then restart Claude Code (or open `/plugin` once) so the hook activates. No files to copy.

## Verify

Ask Claude to read `.env` — it should be denied with a message pointing to `.env.example`.
Reading `.env.example` still works. Ask it to run a script that calls `load_dotenv()` — that is
denied as well.

## Requirements

- **Python 3 on `PATH`** — the hook runs `python3` (no third-party packages).
- **Windows** — the Microsoft Store build creates `python3.exe`, so the hook works as-is. The
  python.org installer instead provides `python` and the `py` launcher (no `python3.exe`); if
  `python3` is not recognized, edit `env-guard/hooks/hooks.json` and change `"command": "python3"`
  to `"command": "python"` (or `"command": "py"`).

The guard is pure Python 3, and the hook uses the exec form (`command` + `args`) so Claude Code
substitutes `${CLAUDE_PLUGIN_ROOT}` itself — no shell involved — and it runs identically on macOS,
Linux, and Windows (with or without Git Bash).

## Repo layout

```
.claude-plugin/marketplace.json   # marketplace manifest (lists the plugin)
env-guard/
├── .claude-plugin/plugin.json    # plugin manifest (holds the version)
└── hooks/
    ├── hooks.json                # registers the PreToolUse hook
    └── block-env.py              # the guard logic
```

## License

MIT
