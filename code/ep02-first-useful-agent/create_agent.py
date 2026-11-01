"""Create (or add a version to) the fact-checker agent: a prompt agent on the Microsoft Copilot harness.

It defines the same agent we build in the Foundry portal in Episode 2:
  - model:        a deployed model that supports reasoning and tool calling
  - instructions: the job (instructions.md)
  - skill:        a repeatable method (skills/fact-check/SKILL.md)
  - tools:        harness tools: web, file read and file write on; shell and subagents off

Run:  python create_agent.py
"""

import os
from pathlib import Path

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    MicrosoftCopilotHarness,
    MicrosoftCopilotToolsetConfig,
    MicrosoftCopilotToolsetPreview,
    PromptAgentDefinition,
    Reasoning,
    SkillInlineContent,
    SkillReference,
)
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

HERE = Path(__file__).parent


def read_skill(path: Path) -> tuple[str, str, str]:
    """Split SKILL.md into (name, description, instructions)."""
    text = path.read_text(encoding="utf-8")
    _, front, body = text.split("---", 2)
    fields = dict(line.split(":", 1) for line in front.strip().splitlines())
    return fields["name"].strip(), fields["description"].strip(), body.strip()


def build_definition(model: str, instructions: str, skill: SkillReference) -> PromptAgentDefinition:
    return PromptAgentDefinition(
        model=model,
        instructions=instructions,
        harness=MicrosoftCopilotHarness(),  # chosen when the agent is created
        skills=[skill],
        reasoning=Reasoning(effort="low"),  # the portal's default for new agents
        tools=[
            # Harness tools are on by default; turn off what this agent doesn't need.
            MicrosoftCopilotToolsetPreview(
                configs=[
                    MicrosoftCopilotToolsetConfig(name="shell", enabled=False),
                    MicrosoftCopilotToolsetConfig(name="subagents", enabled=False),
                ],
            )
        ],
    )


def main() -> None:
    load_dotenv()
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    model = os.environ["MODEL_DEPLOYMENT"]
    agent_name = os.environ.get("AGENT_NAME", "fact-checker")

    skill_name, skill_description, skill_instructions = read_skill(HERE / "skills" / "fact-check" / "SKILL.md")
    instructions = (HERE / "instructions.md").read_text(encoding="utf-8").strip()

    with (
        DefaultAzureCredential(process_timeout=60) as credential,  # the Azure CLI can take a while to start
        AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project,
    ):
        skill = project.beta.skills.create(
            name=skill_name,
            inline_content=SkillInlineContent(description=skill_description, instructions=skill_instructions),
            default=True,
        )
        print(f"Skill:  {skill.name} version {skill.version}")

        agent = project.agents.create_version(
            agent_name=agent_name,
            definition=build_definition(model, instructions, SkillReference(name=skill.name, version=skill.version)),
        )
        print(f"Agent:  {agent.name} version {agent.version}")


if __name__ == "__main__":
    main()
