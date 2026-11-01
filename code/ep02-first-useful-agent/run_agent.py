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


def main() -> int:
    load_dotenv()
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    agent_name = os.environ.get("AGENT_NAME", "fact-checker")
    claims = Path(sys.argv[1] if len(sys.argv) > 1 else HERE / "claims.md").read_text(encoding="utf-8")

    with (
        DefaultAzureCredential() as credential,
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
        for file_id in generated_file_ids(response):
            name = Path(files.files.retrieve(file_id).filename).name
            (HERE / "output").mkdir(exist_ok=True)
            target = HERE / "output" / name
            target.write_bytes(files.files.content(file_id).read())
            print(f"Downloaded: {target.relative_to(HERE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
