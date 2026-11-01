"""Offline checks: the files parse and the agent definition matches what the portal agent shows. No Azure calls.

Run:  python smoke_test.py
"""

from pathlib import Path

from azure.ai.projects.models import SkillReference

from create_agent import HERE, build_definition, read_skill


def main() -> None:
    name, description, body = read_skill(HERE / "skills" / "fact-check" / "SKILL.md")
    assert name == "fact-check" and description and "Verdict" not in name
    assert all(v in body for v in ("Supported", "Contradicted", "Not found")), "verdicts missing from the skill"

    instructions = (HERE / "instructions.md").read_text(encoding="utf-8")
    assert "report.md" in instructions

    claims = (HERE / "claims.md").read_text(encoding="utf-8")
    assert claims.count("Source: https://learn.microsoft.com/") == 4

    definition = build_definition("gpt-5.4-mini", instructions, SkillReference(name=name, version="1")).as_dict()
    assert definition["kind"] == "prompt"
    assert definition["harness"] == {"type": "microsoft_copilot_preview"}
    assert definition["skills"] == [{"name": "fact-check", "version": "1"}]
    (toolset,) = definition["tools"]
    assert toolset["type"] == "microsoft_copilot_toolset_preview"
    assert toolset["default_config"] == {"enabled": False}
    enabled = {c["name"] for c in toolset["configs"] if c["enabled"]}
    assert enabled == {"web", "filesystem_read", "filesystem_write"}, enabled
    print("smoke test passed")


if __name__ == "__main__":
    main()
