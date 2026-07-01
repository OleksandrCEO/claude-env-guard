#!/usr/bin/env python3
"""PreToolUse guard: block all access to the real .env file.

Blocks:
  - Read / Edit / Write on a file named exactly ".env"
  - Bash commands that reference ".env" (cat, grep, less, head, tail, sed, awk, nano, vim, ...)

Allows templates: .env.example, .env.local, .env.* — anything after ".env." is fine.
Rationale: .env holds live secrets. New/changed vars belong in .env.example instead.

Fails open on malformed input so a bad payload never breaks the whole tool pipeline.
"""
import json
import os
import re
import sys

# ".env" token not followed by "." (so .env.example passes) and not part of a longer word.
_ENV_REF = re.compile(r'(^|[^A-Za-z0-9])\.env([^A-Za-z0-9.]|$)')


def deny(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # fail open — never block on unparseable input

    tool = data.get("tool_name", "")
    tool_input = data.get("tool_input") or {}

    if tool in ("Read", "Edit", "Write"):
        path = tool_input.get("file_path", "") or ""
        if os.path.basename(path) == ".env":
            deny("Access to .env is blocked. Never read or edit .env — put new/changed "
                 "variables in .env.example and tell the user which parameter to copy.")

    elif tool == "Bash":
        cmd = tool_input.get("command", "") or ""
        if _ENV_REF.search(cmd):
            deny("Reading .env via shell is blocked. Never cat/grep/etc the .env file — "
                 "use .env.example instead.")

    sys.exit(0)


if __name__ == "__main__":
    main()
