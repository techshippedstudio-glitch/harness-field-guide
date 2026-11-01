#!/usr/bin/env sh
# Give the agent's own identity the Foundry User role on the project, so the harness can return files.
# Reads FOUNDRY_PROJECT_ENDPOINT and AGENT_NAME from .env. Needs the Azure CLI, signed in with `az login`,
# and permission to create role assignments on the project.
set -eu
. ./.env
AGENT_NAME="${AGENT_NAME:-fact-checker}"
FOUNDRY_USER_ROLE="53ca6127-db72-4b80-b1b0-d745d6d5456d"   # role definition ID (the role was recently renamed)

account="$(printf '%s' "$FOUNDRY_PROJECT_ENDPOINT" | sed -E 's#https://([^.]+)\..*#\1#')"
project="$(printf '%s' "$FOUNDRY_PROJECT_ENDPOINT" | sed -E 's#.*/api/projects/([^/]+).*#\1#')"
project_id="$(az resource list --resource-type Microsoft.CognitiveServices/accounts --name "$account" --query "[0].id" -o tsv)/projects/$project"

principal_id="$(az rest --method GET \
  --url "$FOUNDRY_PROJECT_ENDPOINT/agents/$AGENT_NAME?api-version=v1" \
  --resource "https://ai.azure.com" \
  --query instance_identity.principal_id -o tsv)"

az role assignment create \
  --assignee-object-id "$principal_id" \
  --assignee-principal-type ServicePrincipal \
  --role "$FOUNDRY_USER_ROLE" \
  --scope "$project_id" \
  --output none

echo "Foundry User assigned to the identity of agent $AGENT_NAME on project $project."
