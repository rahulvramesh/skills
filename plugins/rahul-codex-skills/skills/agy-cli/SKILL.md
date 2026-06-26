---
name: agy-cli
description: Use the local `agy` Antigravity CLI as an auxiliary agent for quick answers, second-opinion implementation ideas, design critique, disposable project builds, headless automation, conversation resume, model discovery, plugin validation, or Antigravity-specific CLI workflows.
---

# Antigravity CLI

Use `agy` as a full auxiliary agent, not as the source of authority. Let it use its available tools, MCP servers, project context, file access, and terminal capabilities when the task benefits from them, then verify the result with local repo tools before accepting it.

## Quick Start

Prefer the bundled wrapper for headless calls. Resolve `scripts/agy_headless.py` relative to this skill directory before running it:

```bash
python3 scripts/agy_headless.py \
  --cwd "$PWD" \
  --add-dir "$PWD" \
  "Give a concise second opinion on this implementation plan: ..."
```

For direct CLI use, attach the workspace and grant full permission explicitly:

```bash
agy --add-dir "$PWD" --dangerously-skip-permissions \
  -p "Return a concise critique of this UI direction: ..."
```

## Workflow

1. Run `command -v agy`, `agy --version`, and `agy --help` when the task depends on the installed CLI.
2. Run `agy models` before pinning a model. Use the exact displayed model name; this CLI may not visibly fail for an invalid model name.
3. Use `--add-dir /absolute/path` whenever `agy` should read or write a real repo or project directory.
4. Keep sandboxing off unless the user asks for a scratch-only run. In local testing, file writes without a workspace, or with sandboxing, may land in `~/.gemini/antigravity-cli/scratch` instead of the shell cwd.
5. The bundled wrapper passes `--dangerously-skip-permissions` by default so `agy` can use its tools without permission prompts. It intentionally does not pass `--print-timeout`; pass `--review-permissions` only when the user explicitly wants review mode.
6. Inspect any `agy`-created diff or artifact and run the repo's normal checks before treating the result as done.

## Task Patterns

### Quick Answer Or Critique

Keep the prompt bounded, but leave tools and MCP available:

```bash
python3 scripts/agy_headless.py \
  --cwd "$PWD" \
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
  "Create a small static HTML prototype in this directory. Do not modify anything else."
```

For scratch-only experiments:

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
agy -c -p "Continue with only the missing verification steps."
```

Resume a specific conversation ID:

```bash
agy --conversation <conversation-id> -p "Summarize the prior plan and next action."
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
- Give `agy` full tool permission by default. Use `--review-permissions` only for explicitly constrained runs.
- Do not assume `--sandbox` writes into the repo. Verify where files were created.
- Do not rely on `--model` to reject invalid names. Check `agy models` first.
- Treat `agy` output as a proposal. Inspect files, run tests, and make the final engineering decision locally.
