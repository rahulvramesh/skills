---
name: codex-cli
description: Use the local `codex` CLI as an auxiliary Codex agent for full-permission headless implementation, code review, design critique, repository inspection, JSONL event streaming, MCP/plugin diagnostics, session resume, or Codex-specific CLI workflows.
---

# Codex CLI

Use the local `codex` CLI as a second Codex agent when a task benefits from an additional same-stack headless pass, JSONL event logs, native code-review mode, or Codex-specific diagnostics. Treat its output as a proposal until you verify files, diffs, and tests locally.

## Quick Start

Prefer the bundled wrapper for headless calls. Resolve `scripts/codex_headless.py` relative to this skill directory before running it:

```bash
python3 scripts/codex_headless.py \
  --cwd "$PWD" \
  --add-dir "$PWD" \
  --text \
  "Review this implementation plan and return concrete risks."
```

The wrapper defaults to full-permission agent mode:

- `codex --search exec`
- `--dangerously-bypass-approvals-and-sandbox`
- `--json`
- no wrapper timeout

For direct CLI use:

```bash
codex --search exec \
  --dangerously-bypass-approvals-and-sandbox \
  -C "$PWD" \
  --add-dir "$PWD" \
  --json \
  -o /tmp/codex-last-message.txt \
  "Inspect this repo and return concrete findings."
```

## Workflow

1. Run `codex --version`, `codex --help`, and `codex exec --help` when exact flags matter.
2. Use `-C /absolute/path` or wrapper `--cwd` to set the primary workspace.
3. Use `--add-dir /absolute/path` when additional directories should be writable.
4. Keep `--search` enabled by default so the native web search tool is available.
5. Use full permission by default. Pass wrapper `--review-permissions` only when the user explicitly wants approval/sandbox behavior.
6. Read the wrapper result, inspect changed files or diffs, and run the repo's normal checks before reporting success.

## Task Patterns

### Quick Second Pass

```bash
python3 scripts/codex_headless.py \
  --cwd "$PWD" \
  --add-dir "$PWD" \
  --text \
  "Find correctness and security issues in the current checkout. Return only actionable findings."
```

### File-Editing Experiment

Use a disposable directory or worktree, then verify the result:

```bash
python3 scripts/codex_headless.py \
  --cwd "$PWD" \
  --add-dir "$PWD" \
  --text \
  "Create a small static prototype in this directory, then summarize files changed."
```

### JSONL Event Inspection

Use direct CLI when you want live event logs:

```bash
codex --search exec --dangerously-bypass-approvals-and-sandbox \
  -C "$PWD" --add-dir "$PWD" --json \
  "Run a repository inspection and report findings."
```

Observed JSONL event types include:

- `thread.started`
- `turn.started`
- `item.started`
- `item.completed`
- `turn.completed`

Useful item types include `agent_message`, `command_execution`, `file_change`, and `error`. The CLI may print warning lines alongside JSONL; parse only valid JSON object lines.

### Code Review

Native review mode:

```bash
codex --search exec review \
  --dangerously-bypass-approvals-and-sandbox \
  --json \
  --uncommitted
```

In `codex-cli 0.142.2`, `codex exec review --uncommitted` rejected a custom prompt argument. For custom review instructions, use normal `codex exec` with an explicit review prompt instead of native review flags.

### Resume

```bash
codex exec resume --last \
  --dangerously-bypass-approvals-and-sandbox \
  --json \
  "Continue with the missing verification steps."
```

## Diagnostics

Read-only commands:

```bash
codex doctor --summary --no-color --ascii
codex mcp list
codex plugin list
codex features list
```

`codex mcp list` may print configured server URLs; avoid copying credentials or API keys into chat.

## Guardrails

- Do not run account/configuration mutations unless the user explicitly asks: `codex login`, `codex logout`, `codex update`, `codex mcp add/remove/login/logout`, `codex plugin add/remove`, `codex features enable/disable`, `codex delete`, or `codex archive`.
- Avoid using Codex CLI as the only verification source. Always inspect files/diffs and run local tests yourself when it changes code.
- Use `--ephemeral` for one-off probes when session persistence is not useful.
- Use `--output-last-message <file>` or the wrapper's parsed JSON result for reliable final-answer capture.
- Because this invokes another Codex agent with the same local configuration, treat it as an additional pass, not an independent vendor/model review.
