# Rahul Codex Skills

Reusable Codex skills packaged as an installable plugin and marketplace.

## What Is Included

- `grok-cli`: use the local `grok` CLI as a second-opinion agent for quick solutions, design critique, headless automation, and session inspection.
- `agy-cli`: use the local Antigravity `agy` CLI for quick solutions, design critique, disposable builds, conversation resume, and plugin diagnostics.
- `imagegen`: generate and edit images through the OpenAI Image API using a reproducible bundled CLI.

## Why This Layout

This repo follows the Codex plugin distribution pattern:

```text
.agents/plugins/marketplace.json
plugins/rahul-codex-skills/.codex-plugin/plugin.json
plugins/rahul-codex-skills/skills/<skill-name>/SKILL.md
```

Codex skills are directories anchored by `SKILL.md`, with optional `scripts/`, `references/`, `assets/`, and `agents/` folders. Plugins are the installable distribution unit when skills should be shared with other users or teams.

## Install

Install the plugin directly from the plugin subdirectory:

```bash
codex plugin install https://github.com/rahulvramesh/skills.git#plugins/rahul-codex-skills
```

Or add this repository as a marketplace:

```bash
codex plugin marketplace add https://github.com/rahulvramesh/skills.git
```

If your Codex build expects a local marketplace, clone the repo and add the local marketplace root:

```bash
git clone https://github.com/rahulvramesh/skills.git
codex plugin marketplace add ./skills
```

Restart Codex after installing or updating a plugin if changes do not appear immediately.

## Use

Invoke a skill explicitly:

```text
Use $grok-cli to critique this implementation plan.
Use $agy-cli to get an Antigravity second opinion on this UI.
Use $imagegen to create a product hero image.
```

Codex can also choose a skill implicitly when the user request matches its `description`.

## Validate

Run the repo validator:

```bash
python3 scripts/validate_repo.py
```

If you also have the local Codex plugin validator available, run:

```bash
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/rahul-codex-skills
```

## Notes

- `imagegen` requires `OPENAI_API_KEY` for live API calls.
- `grok-cli` requires the `grok` CLI and a working Grok login.
- `agy-cli` requires the `agy` Antigravity CLI and a working Antigravity login.

## References

- Codex skills: https://developers.openai.com/codex/skills
- Codex plugins: https://developers.openai.com/codex/plugins/build
- Reusable Codex skills: https://developers.openai.com/codex/use-cases/reusable-codex-skills
