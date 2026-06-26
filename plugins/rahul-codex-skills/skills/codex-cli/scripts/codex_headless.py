#!/usr/bin/env python3
"""Run `codex exec` headlessly with full-permission defaults."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


def parse_json_events(output: str) -> tuple[list[dict[str, Any]], list[str]]:
    events: list[dict[str, Any]] = []
    noise: list[str] = []
    for line in output.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            value = json.loads(stripped)
        except json.JSONDecodeError:
            noise.append(line)
            continue
        if isinstance(value, dict):
            events.append(value)
        else:
            noise.append(line)
    return events, noise


def summarize_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    final_messages: list[str] = []
    file_changes: list[dict[str, Any]] = []
    commands: list[dict[str, Any]] = []
    errors: list[str] = []
    thread_id = None
    usage = None

    for event in events:
        if event.get("type") == "thread.started":
            thread_id = event.get("thread_id")
        if event.get("type") == "turn.completed":
            usage = event.get("usage")
        item = event.get("item")
        if not isinstance(item, dict):
            continue
        item_type = item.get("type")
        if event.get("type") == "item.completed" and item_type == "agent_message":
            final_messages.append(str(item.get("text", "")))
        elif item_type == "file_change":
            file_changes.append(item)
        elif item_type == "command_execution":
            commands.append(
                {
                    "command": item.get("command"),
                    "exit_code": item.get("exit_code"),
                    "status": item.get("status"),
                    "output_tail": "\n".join(str(item.get("aggregated_output", "")).splitlines()[-20:]),
                }
            )
        elif item_type == "error":
            errors.append(str(item.get("message", "")))

    return {
        "thread_id": thread_id,
        "final_text": final_messages[-1] if final_messages else "",
        "agent_messages": final_messages,
        "file_changes": file_changes,
        "commands": commands,
        "errors": errors,
        "usage": usage,
        "event_count": len(events),
    }


def read_prompt(args: argparse.Namespace) -> str:
    parts: list[str] = []
    if args.prompt_file:
        parts.append(Path(args.prompt_file).read_text(encoding="utf-8"))
    if args.prompt:
        parts.append(" ".join(args.prompt).strip())
    if not parts:
        raise SystemExit("provide a prompt argument or --prompt-file")
    return "\n\n".join(part for part in parts if part)


def build_command(args: argparse.Namespace, prompt: str, last_message_path: Path) -> list[str]:
    cmd = ["codex"]
    if args.search:
        cmd.append("--search")
    cmd.append("exec")
    if args.model:
        cmd.extend(["--model", args.model])
    if args.full_permission:
        cmd.append("--dangerously-bypass-approvals-and-sandbox")
    if args.bypass_hook_trust:
        cmd.append("--dangerously-bypass-hook-trust")
    if args.cwd:
        cmd.extend(["-C", str(args.cwd)])
    for directory in args.add_dir:
        cmd.extend(["--add-dir", str(directory)])
    if args.skip_git_repo_check:
        cmd.append("--skip-git-repo-check")
    if args.ephemeral:
        cmd.append("--ephemeral")
    for config in args.config:
        cmd.extend(["--config", config])
    cmd.append("--json")
    cmd.extend(["--output-last-message", str(last_message_path)])
    cmd.append(prompt)
    return cmd


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt", nargs="*", help="Prompt text. Omit when using --prompt-file.")
    parser.add_argument("--prompt-file", help="Read prompt text from a file")
    parser.add_argument("--cwd", type=Path, default=Path("."), help="Primary workspace for Codex")
    parser.add_argument("--add-dir", type=Path, action="append", default=[], help="Additional writable directory; repeatable")
    parser.add_argument("--model", help="Model for Codex")
    parser.add_argument("--search", dest="search", action="store_true", help="Enable native web search; this is the default.")
    parser.add_argument("--no-search", dest="search", action="store_false", help="Disable native web search.")
    parser.set_defaults(search=True)
    parser.add_argument("--full-permission", dest="full_permission", action="store_true", help="Bypass approvals and sandbox; this is the default.")
    parser.add_argument("--review-permissions", dest="full_permission", action="store_false", help="Do not bypass approvals/sandbox.")
    parser.set_defaults(full_permission=True)
    parser.add_argument("--bypass-hook-trust", action="store_true", help="Pass --dangerously-bypass-hook-trust")
    parser.add_argument("--skip-git-repo-check", action="store_true", help="Allow running outside a git repository")
    parser.add_argument("--ephemeral", action="store_true", help="Do not persist session files")
    parser.add_argument("--config", action="append", default=[], help="Codex config override; repeatable")
    parser.add_argument("--last-message-file", type=Path, help="Where to write Codex's final message")
    parser.add_argument("--raw", action="store_true", help="Print raw Codex stdout/stderr")
    parser.add_argument("--text", action="store_true", help="Print only the final assistant message")
    args = parser.parse_args()

    prompt = read_prompt(args)
    cwd = args.cwd.expanduser().resolve()
    if not cwd.is_dir():
        raise SystemExit(f"cwd does not exist or is not a directory: {cwd}")
    args.cwd = cwd
    args.add_dir = [directory.expanduser().resolve() for directory in args.add_dir]

    temp_path: Path | None = None
    if args.last_message_file:
        last_message_path = args.last_message_file.expanduser().resolve()
        last_message_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        handle = tempfile.NamedTemporaryFile(prefix="codex-last-message-", suffix=".txt", delete=False)
        handle.close()
        temp_path = Path(handle.name)
        last_message_path = temp_path

    cmd = build_command(args, prompt, last_message_path)
    try:
        completed = subprocess.run(
            cmd,
            cwd=str(cwd),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=None,
        )
    except FileNotFoundError:
        print("codex CLI not found on PATH", file=sys.stderr)
        return 127

    if args.raw:
        sys.stderr.write(completed.stderr)
        sys.stdout.write(completed.stdout)
        return completed.returncode

    events, noise = parse_json_events(completed.stdout)
    summary = summarize_events(events)
    if last_message_path.exists():
        last_text = last_message_path.read_text(encoding="utf-8").strip()
        if last_text:
            summary["final_text"] = last_text

    if temp_path:
        temp_path.unlink(missing_ok=True)

    if args.text:
        print(str(summary.get("final_text", "")))
    else:
        print(
            json.dumps(
                {
                    "ok": completed.returncode == 0,
                    "returncode": completed.returncode,
                    "summary": summary,
                    "stdout_noise_tail": noise[-20:],
                    "stderr_tail": completed.stderr.splitlines()[-20:],
                },
                indent=2,
            )
        )

    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
