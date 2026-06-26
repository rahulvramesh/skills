#!/usr/bin/env python3
"""Small wrapper for repeatable Antigravity CLI headless calls."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def read_prompt(args: argparse.Namespace) -> str:
    parts: list[str] = []
    if args.prompt_file:
        parts.append(Path(args.prompt_file).read_text(encoding="utf-8"))
    if args.prompt:
        parts.append(args.prompt)
    if not parts:
        raise SystemExit("provide a prompt argument or --prompt-file")
    return "\n\n".join(part.strip() for part in parts if part.strip())


def build_command(args: argparse.Namespace, prompt: str) -> list[str]:
    cmd = ["agy", "--print-timeout", args.timeout]
    if args.model:
        cmd.extend(["--model", args.model])
    for directory in args.add_dir:
        cmd.extend(["--add-dir", directory])
    if args.project:
        cmd.extend(["--project", args.project])
    if args.new_project:
        cmd.append("--new-project")
    if args.continue_latest:
        cmd.append("--continue")
    if args.conversation:
        cmd.extend(["--conversation", args.conversation])
    if args.sandbox:
        cmd.append("--sandbox")
    if args.auto_approve:
        cmd.append("--dangerously-skip-permissions")
    cmd.extend(["--print", prompt])
    return cmd


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt", nargs="?", help="Prompt text for agy")
    parser.add_argument("--prompt-file", help="Read prompt text from a file")
    parser.add_argument("--cwd", default=".", help="Working directory for agy")
    parser.add_argument("--add-dir", action="append", default=[], help="Workspace directory to attach; repeatable")
    parser.add_argument("--model", help="Exact model name from `agy models`")
    parser.add_argument("--timeout", default="90s", help="agy print timeout, for example 90s or 2m")
    parser.add_argument("--project", help="Antigravity project ID")
    parser.add_argument("--new-project", action="store_true", help="Create a new Antigravity project")
    parser.add_argument("--continue", dest="continue_latest", action="store_true", help="Continue the latest conversation")
    parser.add_argument("--conversation", help="Resume a specific conversation ID")
    parser.add_argument("--sandbox", action="store_true", help="Run with Antigravity sandbox restrictions")
    parser.add_argument("--auto-approve", action="store_true", help="Pass --dangerously-skip-permissions")
    args = parser.parse_args()

    prompt = read_prompt(args)
    cwd = Path(args.cwd).expanduser().resolve()
    if not cwd.is_dir():
        raise SystemExit(f"cwd does not exist or is not a directory: {cwd}")

    cmd = build_command(args, prompt)
    try:
        completed = subprocess.run(cmd, cwd=str(cwd), text=True, check=False)
    except FileNotFoundError:
        print("agy CLI not found on PATH", file=sys.stderr)
        return 127
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
