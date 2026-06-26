---
name: agy-cli
description: Use the local `agy` Antigravity CLI as an auxiliary agent for quick answers, second-opinion implementation ideas, design critique, disposable project builds, headless automation, conversation resume, model discovery, plugin validation, or Antigravity-specific CLI workflows.
---

# Antigravity CLI

Use `agy` as a second agent, not as the source of authority. Let it produce alternatives, critique implementation or UI direction, or do disposable work in a bounded workspace, then verify the result with local repo tools before accepting it.

## Quick Start

Prefer the bundled wrapper for headless calls. Resolve `scripts/agy_headless.py` relative to this skill directory before running it:

```bash
python3 scripts/agy_headless.py \
  --cwd "$PWD" \
  --add-dir "$PWD" \
  --timeout 90s \
  "Give a concise second opinion on this implementation plan: ..."
```

For direct CLI use:

```bash
agy --print-timeout 90s --add-dir "$PWD" \
  -p "Return a concise critique of this UI direction: ..."
```

## Workflow

1. Run `command -v agy`, `agy --version`, and `agy --help` when the task depends on the installed CLI.
2. Run `agy models` before pinning a model. Use the exact displayed model name; this CLI may not visibly fail for an invalid model name.
3. Use `--add-dir /absolute/path` whenever `agy` should read or write a real repo or project directory.
4. Use `--sandbox` for safe experiments where scratch output is acceptable. In local testing, file writes without a workspace, or with sandboxing, may land in `~/.gemini/antigravity-cli/scratch` instead of the shell cwd.
5. Use `--dangerously-skip-permissions` only in a disposable folder, scratch project, or git worktree, and only when the user asked for an automated build/edit run.
6. Inspect any `agy`-created diff or artifact and run the repo's normal checks before treating the result as done.

## Task Patterns

### Quick Answer Or Critique

Keep the prompt bounded and ask for a short, ranked answer:

```bash
python3 scripts/agy_headless.py \
  --cwd "$PWD" \
  --timeout 90s \
  "Find the simplest robust fix for: <problem>. Return bullets with risks."
```

### Design Review

Give `agy` the audience, product type, constraints, and paths to any relevant files or screenshots. Ask for concrete issues and a revised direction, not generic inspiration.

```bash
python3 scripts/agy_headless.py \
  --cwd "$PWD" \
  --add-dir "$PWD" \
  --model "Gemini 3.5 Flash (Low)" \
  --prompt-file /absolute/path/to/design-brief.md
```

### File-Editing Experiment

Use a disposable directory or worktree. Always pass `--add-dir` for the target directory, then verify local files yourself:

```bash
python3 scripts/agy_headless.py \
  --cwd "$PWD" \
  --add-dir "$PWD" \
  --auto-approve \
  --timeout 2m \
  "Create a small static HTML prototype in this directory. Do not modify anything else."
```

For no-risk scratch experiments:

```bash
python3 scripts/agy_headless.py \
  --cwd "$PWD" \
  --sandbox \
  --auto-approve \
  "Prototype the approach in scratch and summarize the files you created."
```

### Conversation Follow-Up

Continue the most recent conversation:

```bash
agy --print-timeout 90s -c -p "Continue with only the missing verification steps."
```

Resume a specific conversation ID:

```bash
agy --print-timeout 90s --conversation <conversation-id> -p "Summarize the prior plan and next action."
```

Useful state locations:

- `~/.gemini/antigravity-cli/cache/last_conversations.json`
- `~/.gemini/antigravity-cli/conversations/*.db`
- `~/.gemini/antigravity-cli/log/`
- `~/.gemini/antigravity-cli/scratch/`

### Plugin Diagnostics

Antigravity plugins use a root-level `plugin.json`, not Codex's `.codex-plugin/plugin.json` layout. A minimal valid Antigravity plugin has:

```json
{
  "name": "my-plugin",
  "version": "0.0.1",
  "displayName": "My Plugin",
  "description": "What this plugin provides."
}
```

Optional component directories include `skills/`, `agents/`, `commands/`, `mcpServers/`, and `hooks/`. Skills use the same basic shape:

```text
skills/<skill-folder>/SKILL.md
```

Common plugin commands:

```bash
agy plugin validate /path/to/plugin-dir
agy plugin install /path/to/plugin-dir
agy plugin list
agy plugin disable <name>
agy plugin enable <name>
agy plugin uninstall <name>
```

`agy plugin list` returns JSON. Installed plugins are stored under `~/.gemini/config/plugins/<plugin-name>`.

## Interactive TUI Notes

Run `agy` for the interactive terminal UI. Useful slash commands include:

- `/add-dir` to attach another workspace directory
- `/skills` to list active skills
- `/mcp` to inspect MCP servers and tools
- `/model` to switch model
- `/permissions` to manage tool rules
- `/diff` to inspect agent changes
- `/tasks` to view task progress
- `/resume`, `/switch`, or `/conversation` to resume past sessions
- `/usage` or `/quota` to inspect quota

The CLI ships a built-in Antigravity guide at `~/.gemini/antigravity-cli/builtin/skills/antigravity_guide` when available.

## Guardrails

- Do not run mutating commands unless the user explicitly asked for them: `agy update`, `agy install`, `agy plugin import`, `agy plugin install`, `agy plugin uninstall`, `agy plugin enable`, or `agy plugin disable`.
- Do not use `--dangerously-skip-permissions` in an important repo unless the target is a disposable worktree or the user explicitly requested it.
- Do not assume `--sandbox` writes into the repo. Verify where files were created.
- Do not rely on `--model` to reject invalid names. Check `agy models` first.
- Treat `agy` output as a proposal. Inspect files, run tests, and make the final engineering decision locally.
