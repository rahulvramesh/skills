---
name: grok-cli
description: Use the local `grok` CLI as an auxiliary agent for quick answers, second-opinion implementation ideas, design critique, disposable project builds, headless automation, session export/inspection, model discovery, MCP/plugin/worktree diagnostics, or Grok-specific CLI workflows. Trigger when the user asks to use Grok, compare against Grok, get a fast alternate solution, run a design review with another agent, or operate `grok` commands from Codex.
---

# Grok CLI

Use Grok as a second agent, not as the source of authority. Let it generate alternatives, critique UI/product decisions, or draft implementation approaches, then verify the result locally before acting on it.

## Quick Start

Prefer the bundled wrapper for headless calls because raw `grok` output can include noisy stderr from plugin, hook, and MCP discovery. Resolve `scripts/grok_headless.py` relative to this skill directory before running it:

```bash
python3 scripts/grok_headless.py \
  --cwd "$PWD" \
  --tools "" \
  --text \
  "Give a concise second opinion on this implementation plan: ..."
```

For direct CLI use, keep fast runs serial and low scope:

```bash
grok --no-wait-for-background --max-turns 1 --disable-web-search --no-subagents --no-memory \
  --output-format json \
  -p "Return a concise critique of this UI direction: ..."
```

Do not pass `--effort` to the default `grok-composer-2.5-fast` model unless `grok models` or a current test confirms the selected model supports reasoning effort.

## Workflow

1. Run `grok --version` and `grok models` when the task depends on current capabilities.
2. Run `grok inspect --json` when configuration, available skills, agents, plugins, MCP servers, or project trust matters.
3. Use `scripts/grok_headless.py` for quick second opinions, design critiques, naming/strategy alternatives, and structured JSON/text output.
4. Use prompt files for long briefs instead of huge shell-quoted prompts.
5. Use a disposable `work/` project or a git worktree before allowing Grok to edit files.
6. Verify Grok-created code, designs, or files with the repo's normal tools. Treat Grok output as a proposal until validated.

## Task Patterns

### Quick Solution

Use one serial headless request, no web, no subagents, no memory:

```bash
python3 scripts/grok_headless.py \
  --text \
  "Find the simplest robust fix for: <problem>. Return bullets with risks."
```

### Design Critique

Give Grok the target user, product type, constraints, and screenshots/files if available. Ask for specific output, such as ranked issues, missing states, or a revised control layout. Do not ask for generic inspiration.

```bash
python3 scripts/grok_headless.py \
  --tools "" \
  --prompt-file /absolute/path/to/design-brief.md \
  --text
```

For no-tool critique, state inside the prompt file that the brief is complete and Grok must answer from the brief only. Otherwise Grok may spend the turn saying it will inspect the workspace.

### File-Editing Experiment

Use a disposable folder or worktree and explicit permissions. Verify diffs afterwards. In this environment, headless file-editing attempts were observed to start an edit but leave no file materialized, even with client-side file flags. Prefer using Grok to produce code/design direction, then apply and verify locally, unless you are intentionally running the interactive Grok UI.

```bash
grok --cwd /absolute/path/to/lab --fs-read --fs-write --terminal \
  --always-approve --permission-mode acceptEdits \
  --background-wait-timeout 60 --max-turns 4 --disable-web-search \
  -p "Create a small static HTML prototype for ..."
```

### Session Follow-Up

Use session commands when a Grok run produced useful state:

```bash
grok sessions list --limit 10
grok export <session-id> /absolute/path/to/session.md
grok -r <session-id> "Continue with only the missing verification steps"
```

## Guardrails

- Avoid mutating commands unless the user explicitly asked for that operation: `grok logout`, `grok memory clear`, `grok sessions delete`, `grok leader kill`, `grok plugin install/update/disable/uninstall`, `grok setup`, `grok update` without `--check`, and destructive worktree commands.
- Avoid parallel Grok model calls; this environment has shown low request-rate limits.
- Prefer `--output-format json` over `streaming-json` for automation. Streaming JSON exposes token events and includes thought events.
- Capture stderr separately for automation. Stderr may contain plugin collision warnings, hook warnings, and MCP auth/timeouts even when the final answer succeeds.
- Use `--check` only when the extra latency is justified.
- If Grok edits files, inspect the diff and run normal tests before accepting the work.
- If a headless file-editing run ends with a planning sentence such as "I'll create..." or `stopReason: Cancelled`, assume no files were written until local verification proves otherwise.

## References

Read `references/cli-reference.md` when command coverage, safe/mutating command classification, output formats, worktrees, MCP/plugins, or observed local quirks matter.
