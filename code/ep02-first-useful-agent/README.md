# Episode 2: your first useful Copilot harness agent

A prompt agent on the Microsoft Copilot harness that fact-checks claims against their cited sources and returns
an evidence-backed `report.md`. It's the same agent we build in the Foundry portal in Episode 2, defined in Python.

| Piece | File | What it contributes |
|---|---|---|
| Instructions | `instructions.md` | The job and the expected output |
| Skill | `skills/fact-check/SKILL.md` | A repeatable method: fetch, find, decide, quote, report |
| Tools | `create_agent.py` (`MicrosoftCopilotToolsetPreview`) | Harness tools are on by default; shell and subagents turned off (web, file read, file write stay on) |
| Harness | `create_agent.py` (`MicrosoftCopilotHarness()`) | Foundry runs the agent loop and the sandbox |
| Input | `claims.md` | Four claims with their Microsoft Learn sources |

Claim 4 in `claims.md` is deliberately incorrect, so the report shows a **Contradicted** verdict with its evidence.

## Prerequisites

- A Microsoft Foundry project in a region that supports the Copilot harness, with a deployed model that supports
  reasoning and tool calling (we use `gpt-5.4-mini`).
- The **Foundry User** role on the project for your own account.
- Python 3.11 or later and the Azure CLI. Tested with `azure-ai-projects` 2.10.0 on Python 3.11, 3.12 and 3.13.

## Run it

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                 # then fill in your project endpoint and model deployment name
az login                             # Microsoft Entra sign-in; no keys anywhere

python smoke_test.py                 # offline check of the definition
python create_agent.py               # creates the skill and the agent (or a new version of each)
```

Before the agent can return `report.md`, give the agent's own identity the **Foundry User** role on the project
(this is separate from your role, and the agent must exist first):

```bash
./assign_agent_role.sh               # Windows: .\assign_agent_role.ps1
```

Allow a few minutes for the role to take effect, then:

```bash
python run_agent.py                  # sends claims.md, waits, downloads output/report.md
```

Open the agent in the Foundry portal (Build > Agents) to see the same agent, its versions and the run's trace.

## Notes

- The harness is chosen when an agent is created. During the preview you can't add it to an existing agent.
- Every request to a harness agent needs a conversation; `run_agent.py` creates one.
- Troubleshooting (model quota, regions, rate limits): see the Episode 2 page on the site.
