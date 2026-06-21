# Installation

## Direct Plugin Install

```bash
codex plugin install https://github.com/rahulvramesh/skills.git#plugins/rahul-codex-skills
```

## Marketplace Install

```bash
codex plugin marketplace add https://github.com/rahulvramesh/skills.git
```

If remote marketplace installation is unavailable in your Codex build, clone the repository and add the local marketplace root:

```bash
git clone https://github.com/rahulvramesh/skills.git
codex plugin marketplace add ./skills
```

## Manual Skill Install

Copy a skill folder into your user skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R plugins/rahul-codex-skills/skills/grok-cli ~/.codex/skills/
```

Restart Codex if newly installed skills do not appear.
