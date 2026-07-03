#!/usr/bin/env python3
"""PreToolUse guard: block all access to the real .env file — including via scripts.

Blocks:
  - Read / Edit / Write on a file named exactly ".env"
  - Write / Edit whose *content* reads .env — a script with open(".env"),
    load_dotenv(), dotenv.config(), etc. (only script-ish target files are scanned)
  - Bash commands that reference ".env" (cat, grep, source, export $(cat .env), ...)
  - Bash commands that run a script file (python foo.py, node app.js, ./run.sh)
    whose on-disk content reads .env

Allows templates: .env.example, .env.local, .env.* — anything after ".env." is fine.
Does NOT block os.getenv / process.env / os.environ: those read the process
environment, not the .env file, and blocking them would flag masses of legit code.
The leak vector is *loading* .env, which is what the dotenv-loader rules catch.

Fails open on malformed input / unreadable files so a bad payload or a missing
file never breaks the whole tool pipeline.
"""
import json
import os
import re
import sys

# ".env" token not followed by "." (so .env.example passes) and not part of a longer word.
_ENV_REF = re.compile(r'(^|[^A-Za-z0-9])\.env([^A-Za-z0-9.]|$)')

# dotenv loaders that default to reading ".env" when given no explicit path.
# python-dotenv / node dotenv / godotenv / phpdotenv / ruby dotenv.
_DOTENV_LOADER = re.compile(
    r'load_dotenv\s*\('
    r'|dotenv\.config\s*\('
    r"|require\(\s*['\"]dotenv"
    r"|from\s+['\"]?dotenv"
    r"|import\s+['\"]?dotenv"
    r'|dotenv/config'
    r'|godotenv\.(?:Load|Overload)'
    r'|Dotenv::(?:load|create)'
)

# File extensions we treat as "a script" — worth scanning contents / reading from disk.
_SCRIPT_EXT = (
    "py", "js", "mjs", "cjs", "ts", "tsx", "sh", "bash", "zsh",
    "rb", "go", "php", "pl", "ps1",
)

# Tokens inside a Bash command that look like a script file path.
_SCRIPT_TOKEN = re.compile(
    r'(?:^|[\s=])((?:\./|\.\./|/)?[\w./\-]+\.(?:' + "|".join(_SCRIPT_EXT) + r'))(?=$|[\s;&|)])'
)

_MAX_READ = 256 * 1024  # don't slurp huge files while scanning


def deny(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def content_reads_env(text: str) -> bool:
    """True if this script text reads the real .env (not a .env.* template)."""
    if _ENV_REF.search(text):
        return True
    for line in text.splitlines():
        # A dotenv loader is suspicious unless it explicitly points at a .env.* template.
        if _DOTENV_LOADER.search(line) and ".env." not in line:
            return True
    return False


def looks_like_script(path: str, text: str) -> bool:
    ext = path.rsplit(".", 1)[-1].lower() if "." in os.path.basename(path) else ""
    if ext in _SCRIPT_EXT:
        return True
    return text.lstrip().startswith("#!")  # shebang


def scan_executed_files(cmd: str, cwd: str) -> str | None:
    """If the command runs a script file that reads .env, return that file's path."""
    for match in _SCRIPT_TOKEN.finditer(cmd):
        rel = match.group(1)
        path = rel if os.path.isabs(rel) else os.path.join(cwd, rel)
        try:
            if os.path.getsize(path) > _MAX_READ:
                continue
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                text = fh.read()
        except OSError:
            continue  # missing / unreadable — fail open
        if content_reads_env(text):
            return rel
    return None


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # fail open — never block on unparseable input

    tool = data.get("tool_name", "")
    tool_input = data.get("tool_input") or {}
    cwd = data.get("cwd") or os.getcwd()

    if tool in ("Read", "Edit", "Write"):
        path = tool_input.get("file_path", "") or ""
        if os.path.basename(path) == ".env":
            deny("Access to .env is blocked. Never read or edit .env — put new/changed "
                 "variables in .env.example and tell the user which parameter to copy.")

        # Scan the content being written into a script for .env access.
        content = (tool_input.get("content") or "") + "\n" + (tool_input.get("new_string") or "")
        if content.strip() and looks_like_script(path, content) and content_reads_env(content):
            deny("This script reads the real .env (open('.env') / load_dotenv() / similar). "
                 "Blocked. Load configuration from .env.example or the process environment "
                 "instead, and never read the live .env file from code.")

    elif tool == "Bash":
        cmd = tool_input.get("command", "") or ""
        if _ENV_REF.search(cmd):
            deny("Reading .env via shell is blocked. Never cat/grep/source/etc the .env file — "
                 "use .env.example instead.")
        hit = scan_executed_files(cmd, cwd)
        if hit:
            deny(f"Blocked: the script '{hit}' this command runs reads the real .env "
                 "(open('.env') / load_dotenv() / similar). Read config from .env.example "
                 "or the process environment instead of the live .env file.")

    sys.exit(0)


if __name__ == "__main__":
    main()
