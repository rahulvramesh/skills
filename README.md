# Rahul Codex Skills

Reusable Codex skills packaged as an installable plugin and marketplace.

## What Is Included

- `grok-cli`: use the local `grok` CLI as a second-opinion agent for quick solutions, design critique, headless automation, and session inspection.
- `imagegen`: generate and edit images through the OpenAI Image API using a reproducible bundled CLI.
- `chronicle`: use Codex Chronicle screen context when the local Chronicle feature is enabled.

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
codex plugin install https://github.com/rahulvramesh/codex-skills.git#plugins/rahul-codex-skills
```

Or add this repository as a marketplace:

```bash
codex plugin marketplace add https://github.com/rahulvramesh/codex-skills.git
```

If your Codex build expects a local marketplace, clone the repo and add the local marketplace root:

```bash
git clone https://github.com/rahulvramesh/codex-skills.git
codex plugin marketplace add ./codex-skills
```

Restart Codex after installing or updating a plugin if changes do not appear immediately.

## Use

Invoke a skill explicitly:

```text
Use $grok-cli to critique this implementation plan.
Use $imagegen to create a product hero image.
Use $chronicle to resolve what I had open recently.
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
- `chronicle` only works when Codex Chronicle is enabled locally.

## References

- Codex skills: https://developers.openai.com/codex/skills
- Codex plugins: https://developers.openai.com/codex/plugins/build
- Reusable Codex skills: https://developers.openai.com/codex/use-cases/reusable-codex-skills
