# Grok CLI Reference

Observed on 2026-06-26 with `grok 0.2.67 (03e13f99286)`. Re-run `grok --help`, `grok version --json`, and `grok models` if exact behavior matters.

## Known Models

`grok models` showed:

- `grok-composer-2.5-fast` as the default model.
- `grok-build`.

The default model rejected `--effort low` with `invalid-argument: Model grok-composer-2.5-fast does not support parameter reasoningEffort`. Omit `--effort` unless the selected model is verified to support it.

## Reliable Baseline Commands

Inspect local configuration:

```bash
grok inspect --json
```

Check version/update state:

```bash
grok version --json
grok update --check --json
```

List models:

```bash
grok models
```

Full-permission headless JSON call:

```bash
grok --cwd "$PWD" --always-approve --permission-mode bypassPermissions --output-format json \
  -p "Return a concise answer to: ..."
```

Prompt file:

```bash
grok --cwd "$PWD" --always-approve --permission-mode bypassPermissions --output-format json \
  --prompt-file /absolute/path/to/prompt.md
```

Long-running implementation in a disposable folder:

```bash
grok --cwd /absolute/path/to/lab --fs-read --fs-write --terminal \
  --always-approve --permission-mode bypassPermissions \
  -p "Implement this prototype, then summarize created files and verification."
```

## Output Formats

- `plain`: human text. Harder to parse in automation.
- `json`: one JSON object with fields observed as `text`, `stopReason`, `sessionId`, `requestId`, and `thought`.
- `streaming-json`: NDJSON events. Observed event types include `thought`, `text`, and final `end` with `stopReason`, `sessionId`, and `requestId`.

For Codex automation, use `json` and ignore or strip any `thought` field. Capture stderr separately because warnings are noisy.

## Top-Level Options Worth Using

- `--cwd <CWD>`: run against a specific project.
- `-p, --single <PROMPT>`: single-turn headless prompt.
- `--prompt-file <PATH>`: use for long briefs.
- `--prompt-json <JSON>`: content-block input for structured/multimodal capable workflows.
- `--output-format plain|json|streaming-json`: choose parseability.
- `--model <MODEL>`: select `grok-build` or another listed model.
- `--max-turns <N>`: bound cost and time when a constrained run is explicitly wanted.
- `--no-wait-for-background`: return after the first turn instead of waiting for background work.
- `--disable-web-search`: opt out of web tools for explicitly local-only work.
- `--no-subagents`: opt out of subagent fan-out for explicitly constrained calls.
- `--no-memory`: opt out of cross-session memory.
- `--check`: append a self-verification loop for headless work.
- `--always-approve` and `--permission-mode bypassPermissions`: grant full tool permission for autonomous runs.
- `--worktree [NAME]`: start in a new git worktree.
- `--continue`, `--resume [SESSION_ID]`, `--restore-code`: continue previous work.
- `--rules <RULES>` and `--system-prompt-override <PROMPT>`: shape behavior when required.
- `--tools <TOOLS>` and `--disallowed-tools <TOOLS>`: restrict built-in tool access only when a constrained run is explicitly wanted.
- `--tools ""`: observed to be accepted as an explicit empty tool allowlist; do not use by default.

Completion output exposed additional hidden/compatibility flags such as `--storage-mode`, `--client-identifier`, `--hunk-tracker-mode`, `--terminal`, `--fs-read`, `--fs-write`, `--no-ask-user`, `--force-login`, and `--no-auto-update`. Verify with the installed version before relying on them.

## Command Map

Read-only or usually safe:

- `grok --help`, `grok help <command>`, `grok version`, `grok version --json`
- `grok inspect --json`
- `grok models`
- `grok sessions list --limit N`
- `grok sessions search <query>`
- `grok export <session-id> [output]`
- `grok trace --local <session-id> -o <output>`
- `grok update --check --json`
- `grok leader list`
- `grok mcp list --json`
- `grok mcp doctor [name] --json`
- `grok plugin list --json`
- `grok plugin details <name>`
- `grok plugin marketplace list`
- `grok worktree list`
- `grok worktree show <id-or-name>`
- `grok completions zsh|bash|fish|powershell|elvish`

Mutating or explicit-user-intent commands:

- `grok login`, `grok logout`
- `grok setup`
- `grok update` without `--check`
- `grok mcp add/remove`
- `grok plugin install/uninstall/update/enable/disable/tag`
- `grok plugin marketplace add/remove/update`
- `grok sessions delete`
- `grok memory clear`
- `grok leader kill`
- `grok leader profile start/stop`
- `grok worktree rm/gc/db rebuild`

Advanced integration:

- `grok agent stdio`: run the agent over stdio.
- `grok agent headless`: run headlessly over Grok WebSocket relay.
- `grok agent serve`: expose a local WebSocket server, default bind `127.0.0.1:2419`.
- `grok agent leader`: run a shared leader process.
- `grok dashboard`: open the dashboard UI.
- `grok ssh <ssh args>`: run ssh with local clipboard support.

## Local Observations

- `grok inspect --json` returned the richest discovery result: version/channel, project trust, inherited Claude/Cursor instructions, permissions, hooks, skills, agents, plugins, marketplaces, MCP servers, config sources, and compatibility surfaces.
- `grok mcp list --json` and `grok plugin list --json` returned empty arrays in the same workspace even though `inspect --json` showed imported compatibility entries. Use `inspect --json` for full discovery; use subcommands for Grok-native config.
- Headless runs emitted many stderr warnings from plugin name collisions, hook parsing, MCP OAuth requirements, and MCP timeouts. Successful JSON output still appeared on stdout.
- For design prompt files, include workspace paths and let Grok inspect files when that can improve the critique. Use answer-only language only for intentionally constrained runs.
- A 2026-06-26 full-permission headless run through `scripts/grok_headless.py` successfully created `grok_full_permission_probe.txt` in a disposable `--cwd` directory. Verify created files after each run, but do not assume headless edits are unavailable.
- Parallel model calls hit a `429 Too Many Requests` response at a 2 RPS limit. Keep calls serial.
- `grok leader list` reported no leader candidates.
- `grok update --check --json` reported `updateAvailable: false` for version `0.2.59`.
