#!/usr/bin/env python3
"""Validate the public Codex skills repository structure."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "rahul-codex-skills"
SKILLS = PLUGIN / "skills"
MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"{path.relative_to(ROOT)} is not valid JSON: {exc}")


def validate_plugin() -> None:
    manifest_path = PLUGIN / ".codex-plugin" / "plugin.json"
    if not manifest_path.exists():
        fail("missing plugins/rahul-codex-skills/.codex-plugin/plugin.json")
    manifest = load_json(manifest_path)

    for field in ("name", "version", "description", "author", "skills", "interface"):
        if field not in manifest:
            fail(f"plugin.json missing {field}")
    if manifest["name"] != "rahul-codex-skills":
        fail("plugin.json name must be rahul-codex-skills")
    if not re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"]):
        fail("plugin.json version must be strict semver")
    if manifest["skills"] != "./skills/":
        fail("plugin.json skills must be ./skills/")
    if not (PLUGIN / "skills").is_dir():
        fail("plugin skills directory missing")


def validate_marketplace() -> None:
    if not MARKETPLACE.exists():
        fail("missing .agents/plugins/marketplace.json")
    marketplace = load_json(MARKETPLACE)
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        fail("marketplace plugins must be a non-empty list")
    entry = next((item for item in plugins if item.get("name") == "rahul-codex-skills"), None)
    if entry is None:
        fail("marketplace missing rahul-codex-skills entry")
    source = entry.get("source", {})
    if source.get("source") not in {"local", "git-subdir"}:
        fail("marketplace source must be local or git-subdir")
    if source.get("path") != "./plugins/rahul-codex-skills":
        fail("marketplace source path must point to ./plugins/rahul-codex-skills")
    policy = entry.get("policy", {})
    if policy.get("installation") != "AVAILABLE":
        fail("marketplace policy.installation must be AVAILABLE")
    if policy.get("authentication") != "ON_INSTALL":
        fail("marketplace policy.authentication must be ON_INSTALL")
    if "category" not in entry:
        fail("marketplace entry missing category")


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"{path.relative_to(ROOT)} missing YAML frontmatter")
    end = text.find("\n---", 4)
    if end == -1:
        fail(f"{path.relative_to(ROOT)} has unterminated YAML frontmatter")
    frontmatter = text[4:end]
    parsed: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if not line.strip() or line.startswith(" "):
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            parsed[key.strip()] = value.strip().strip('"')
    return parsed


def validate_skills() -> None:
    if not SKILLS.is_dir():
        fail("skills directory missing")
    skill_dirs = sorted(path for path in SKILLS.iterdir() if path.is_dir())
    if not skill_dirs:
        fail("no skills found")
    for skill_dir in skill_dirs:
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            fail(f"{skill_dir.relative_to(ROOT)} missing SKILL.md")
        frontmatter = parse_frontmatter(skill_file)
        name = frontmatter.get("name")
        description = frontmatter.get("description")
        if not name:
            fail(f"{skill_file.relative_to(ROOT)} missing name")
        if name != skill_dir.name:
            fail(f"{skill_file.relative_to(ROOT)} name does not match folder")
        if not description:
            fail(f"{skill_file.relative_to(ROOT)} missing description")


def scan_for_private_paths() -> None:
    forbidden = (
        ("/Users/rahulvramesh", "private absolute path"),
        ("gho_[A-Za-z0-9_]{20,}", "GitHub token"),
        ("sk-[A-Za-z0-9]{20,}", "OpenAI API key"),
        ("BEGIN [A-Z ]*PRIVATE KEY", "private key"),
    )
    self_path = Path(__file__).resolve()
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or ".venv" in path.parts:
            continue
        if path.resolve() == self_path:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern, label in forbidden:
            if re.search(pattern, text):
                fail(f"{path.relative_to(ROOT)} contains forbidden token: {label}")


def main() -> int:
    validate_plugin()
    validate_marketplace()
    validate_skills()
    scan_for_private_paths()
    print("Repository structure is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
