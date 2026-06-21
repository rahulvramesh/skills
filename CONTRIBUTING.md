# Contributing

## Add Or Update A Skill

1. Put the skill under `plugins/rahul-codex-skills/skills/<skill-name>/`.
2. Keep `SKILL.md` frontmatter minimal:

```yaml
---
name: skill-name
description: Clear trigger and scope.
---
```

3. Put reusable commands in `scripts/`, longer docs in `references/`, templates in `assets/`, and UI metadata in `agents/openai.yaml`.
4. Avoid absolute local paths and secrets.
5. Run:

```bash
python3 scripts/validate_repo.py
```
