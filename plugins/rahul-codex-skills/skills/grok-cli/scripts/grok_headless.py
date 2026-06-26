#!/usr/bin/env python3
"""Run `grok` headlessly with full-agent defaults and clean parsing."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def stderr_tail(stderr: str, max_lines: int) -> list[str]:
    lines = [line for line in stderr.splitlines() if line.strip()]
    return lines[-max_lines:]


def parse_streaming_json(stdout: str) -> dict[str, object]:
    text_parts: list[str] = []
    end: dict[str, object] = {}
    events = 0
    for line in stdout.splitlines():
        if not line.strip():
            continue
        events += 1
        event = json.loads(line)
        if event.get("type") == "text":
            text_parts.append(str(event.get("data", "")))
        elif event.get("type") == "end":
            end = event
    return {
        "text": "".join(text_parts),
        "stopReason": end.get("stopReason"),
        "sessionId": end.get("sessionId"),
        "requestId": end.get("requestId"),
        "eventCount": events,
    }


def build_command(args: argparse.Namespace) -> list[str]:
    cmd = ["grok"]
    if args.cwd:
        cmd.extend(["--cwd", str(args.cwd)])
    if args.model:
        cmd.extend(["--model", args.model])
    if not args.wait_background:
        cmd.append("--no-wait-for-background")
    if args.max_turns is not None:
        cmd.extend(["--max-turns", str(args.max_turns)])
    if not args.web_search:
        cmd.append("--disable-web-search")
    if not args.subagents:
        cmd.append("--no-subagents")
    if not args.memory:
        cmd.append("--no-memory")
    if args.experimental_memory:
        cmd.append("--experimental-memory")
    if args.check:
        cmd.append("--check")
    if args.full_permission:
        args.always_approve = True
        if not args.permission_mode:
            args.permission_mode = "bypassPermissions"
    if args.always_approve:
        cmd.append("--always-approve")
    if args.permission_mode:
        cmd.extend(["--permission-mode", args.permission_mode])
    if args.tools is not None:
        cmd.extend(["--tools", args.tools])
    if args.disallowed_tools is not None:
        cmd.extend(["--disallowed-tools", args.disallowed_tools])
    if args.rules:
        cmd.extend(["--rules", args.rules])
    if args.verbatim:
        cmd.append("--verbatim")
    cmd.extend(["--output-format", args.output_format])

    if args.prompt_file:
        cmd.extend(["--prompt-file", str(args.prompt_file)])
    elif args.prompt_json:
        cmd.extend(["--prompt-json", args.prompt_json])
    else:
        prompt = " ".join(args.prompt).strip()
        if not prompt:
            raise SystemExit("Provide a prompt, --prompt-file, or --prompt-json.")
        cmd.extend(["-p", prompt])
    return cmd


def main() -> int:
    parser = argparse.ArgumentParser(description="Headless Grok wrapper for Codex workflows.")
    parser.add_argument("prompt", nargs="*", help="Prompt text. Omit when using --prompt-file or --prompt-json.")
    parser.add_argument("--cwd", type=Path, help="Working directory for Grok.")
    parser.add_argument("--model", help="Model ID, for example grok-build.")
    parser.add_argument("--prompt-file", type=Path, help="Prompt file path.")
    parser.add_argument("--prompt-json", help="JSON content blocks for Grok.")
    parser.add_argument("--output-format", choices=["plain", "json", "streaming-json"], default="json")
    parser.add_argument("--max-turns", type=int, default=None)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--background-wait", dest="wait_background", action="store_true", help="Wait for background work; this is the default.")
    parser.add_argument("--no-wait-for-background", dest="wait_background", action="store_false", help="Return without waiting for background work.")
    parser.set_defaults(wait_background=True)
    parser.add_argument("--allow-web-search", dest="web_search", action="store_true", help="Allow web tools; this is the default.")
    parser.add_argument("--disable-web-search", dest="web_search", action="store_false", help="Disable web search/fetch tools.")
    parser.set_defaults(web_search=True)
    parser.add_argument("--allow-subagents", dest="subagents", action="store_true", help="Allow subagents; this is the default.")
    parser.add_argument("--no-subagents", dest="subagents", action="store_false", help="Disable subagent spawning.")
    parser.set_defaults(subagents=True)
    parser.add_argument("--memory", dest="memory", action="store_true", help="Allow Grok memory; this is the default.")
    parser.add_argument("--no-memory", dest="memory", action="store_false", help="Disable Grok memory for this run.")
    parser.set_defaults(memory=True)
    parser.add_argument("--experimental-memory", action="store_true", help="Pass Grok's --experimental-memory flag.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--full-permission", dest="full_permission", action="store_true", help="Auto-approve tools and use bypassPermissions; this is the default.")
    parser.add_argument("--review-permissions", dest="full_permission", action="store_false", help="Do not auto-approve tools by default.")
    parser.set_defaults(full_permission=True)
    parser.add_argument("--always-approve", action="store_true")
    parser.add_argument("--permission-mode", choices=["default", "acceptEdits", "auto", "dontAsk", "bypassPermissions", "plan"])
    parser.add_argument("--tools")
    parser.add_argument("--disallowed-tools")
    parser.add_argument("--rules")
    parser.add_argument("--verbatim", action="store_true")
    parser.add_argument("--stderr-file", type=Path, help="Write Grok stderr to this path.")
    parser.add_argument("--stderr-lines", type=int, default=20)
    parser.add_argument("--raw", action="store_true", help="Print raw stdout and forward stderr.")
    parser.add_argument("--text", action="store_true", help="Print only response text.")
    args = parser.parse_args()

    cmd = build_command(args)
    run_cwd = str(args.cwd) if args.cwd else None
    try:
        completed = subprocess.run(
            cmd,
            cwd=run_cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=args.timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        payload = {
            "ok": False,
            "error": f"grok timed out after {args.timeout}s",
            "stdout": exc.stdout or "",
            "stderrTail": stderr_tail(exc.stderr or "", args.stderr_lines),
            "command": cmd,
        }
        print(json.dumps(payload, indent=2))
        return 124

    if args.stderr_file:
        args.stderr_file.parent.mkdir(parents=True, exist_ok=True)
        args.stderr_file.write_text(completed.stderr, encoding="utf-8")

    if args.raw:
        sys.stderr.write(completed.stderr)
        sys.stdout.write(completed.stdout)
        return completed.returncode

    parsed: dict[str, object]
    try:
        if args.output_format == "json":
            parsed = json.loads(completed.stdout)
            parsed.pop("thought", None)
        elif args.output_format == "streaming-json":
            parsed = parse_streaming_json(completed.stdout)
        else:
            parsed = {"text": completed.stdout}
    except Exception as exc:  # Keep raw output available for debugging bad JSON.
        parsed = {"parseError": str(exc), "stdout": completed.stdout}

    if args.text and "text" in parsed:
        print(str(parsed.get("text", "")))
    else:
        payload = {
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "result": parsed,
            "stderrTail": stderr_tail(completed.stderr, args.stderr_lines),
        }
        print(json.dumps(payload, indent=2))

    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
