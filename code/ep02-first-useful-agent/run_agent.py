"""Send claims.md to the fact-checker agent and download the report it writes.

Run:  python run_agent.py            (uses claims.md)
      python run_agent.py my-claims.md
"""

import os
import re
import sys
import time
from pathlib import Path

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

HERE = Path(__file__).parent
REPORT = "report.md"
DOWNLOAD_ID = re.compile(r"Download ID:\**\s*`?([A-Za-z][A-Za-z0-9_-]+)`?", re.IGNORECASE)


def generated_file_ids(response) -> list[str]:
    """File IDs the agent returned: file citations first, then a 'Download ID:' line."""
    ids: list[str] = []
    for item in response.output:
        if item.type != "message":
            continue
        for content in item.content:
            if content.type != "output_text":
                continue
            for note in content.annotations or []:
                if note.type == "file_citation" and note.file_id not in ids:
                    ids.append(note.file_id)
            ids += [m for m in DOWNLOAD_ID.findall(content.text) if m not in ids]
    return ids


def download_files(files, file_ids: list[str], out_dir: Path) -> list[Path]:
    """Download each Foundry File into out_dir. Raises if nothing usable comes back."""
    if not file_ids:
        raise RuntimeError(
            "The agent didn't return a downloadable file. Check that the agent's identity has the "
            "Foundry User role on the project (README: 'Give the agent access'), wait a few minutes, then run again."
        )
    out_dir.mkdir(exist_ok=True)
    saved = []
    for file_id in file_ids:
        name = Path(files.files.retrieve(file_id).filename).name
        data = files.files.content(file_id).read()
        if not data:
            raise RuntimeError(f"Foundry File {file_id} ({name}) is empty.")
        target = out_dir / name
        target.write_bytes(data)
        saved.append(target)
    if not any(p.name == REPORT for p in saved):
        raise RuntimeError(f"The agent returned {[p.name for p in saved]}, but not {REPORT}.")
    return saved


def main() -> int:
    load_dotenv()
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    agent_name = os.environ.get("AGENT_NAME", "fact-checker")
    claims = Path(sys.argv[1] if len(sys.argv) > 1 else HERE / "claims.md").read_text(encoding="utf-8")

    with (
        DefaultAzureCredential(process_timeout=60) as credential,  # the Azure CLI can take a while to start
        AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project,
    ):
        agent = project.get_openai_client(agent_name=agent_name)  # the agent's own endpoint
        conversation = agent.conversations.create()  # the harness needs a conversation
        print(f"Conversation: {conversation.id}")

        started = time.monotonic()
        response = agent.responses.create(conversation=conversation.id, input=claims, background=True)
        while response.status in ("queued", "in_progress"):
            time.sleep(3)
            response = agent.responses.retrieve(response.id)
        print(f"Status: {response.status} after {time.monotonic() - started:.0f} s")
        if response.status != "completed":
            print(response.error, file=sys.stderr)
            return 1

        print(f"\nAgent: {response.output_text}\n")

        files = project.get_openai_client()  # project-level client: Foundry Files
        try:
            saved = download_files(files, generated_file_ids(response), HERE / "output")
        except RuntimeError as error:
            print(f"Error: {error}", file=sys.stderr)
            return 2
        for path in saved:
            print(f"Downloaded: {path.relative_to(HERE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
