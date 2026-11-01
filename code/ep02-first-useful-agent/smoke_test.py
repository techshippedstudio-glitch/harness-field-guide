"""Offline checks: the files parse, the agent definition matches what the portal agent shows, and run_agent
fails when no report comes back. No Azure calls.

Run:  python smoke_test.py
"""

import tempfile
from pathlib import Path
from types import SimpleNamespace

from azure.ai.projects.models import SkillReference

from create_agent import HERE, build_definition, read_skill
from run_agent import download_files


class FakeFiles:
    """Stands in for the Foundry Files client: file_id -> (filename, bytes)."""

    def __init__(self, store: dict[str, tuple[str, bytes]]):
        self.files = self
        self.store = store

    def retrieve(self, file_id):
        return SimpleNamespace(filename=self.store[file_id][0])

    def content(self, file_id):
        return SimpleNamespace(read=lambda: self.store[file_id][1])


def expect_error(files, ids, out_dir, text):
    try:
        download_files(files, ids, out_dir)
    except RuntimeError as error:
        assert text in str(error), error
    else:
        raise AssertionError(f"expected an error containing {text!r}")


def check_downloads() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "output"
        expect_error(FakeFiles({}), [], out, "didn't return a downloadable file")
        expect_error(FakeFiles({"f1": ("report.md", b"")}), ["f1"], out, "is empty")
        expect_error(FakeFiles({"f1": ("notes.txt", b"x")}), ["f1"], out, "not report.md")
        (saved,) = download_files(FakeFiles({"f1": ("/mnt/out/report.md", b"# Fact-check report")}), ["f1"], out)
        assert saved == out / "report.md" and saved.read_bytes() == b"# Fact-check report"


def main() -> None:
    name, description, body = read_skill(HERE / "skills" / "fact-check" / "SKILL.md")
    assert name == "fact-check" and description and "Verdict" not in name
    verdicts = ("Supported", "Contradicted", "Insufficient evidence", "Source unavailable")
    assert all(f"**{v}**" in body for v in verdicts), "verdicts missing from the skill"
    assert "No evidence retrieved" in body and "link to the cited URL" in body

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
    assert "default_config" not in toolset  # harness tools default to on
    disabled = {c["name"] for c in toolset["configs"] if not c["enabled"]}
    assert disabled == {"shell", "subagents"}, disabled
    assert definition["reasoning"] == {"effort": "low"}
    check_downloads()
    print("smoke test passed")


if __name__ == "__main__":
    main()
