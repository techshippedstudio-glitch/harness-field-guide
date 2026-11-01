# Give the agent's own identity the Foundry User role on the project, so the harness can return files.
# Reads FOUNDRY_PROJECT_ENDPOINT and AGENT_NAME from .env. Needs the Azure CLI, signed in with `az login`,
# and permission to create role assignments on the project.
$ErrorActionPreference = "Stop"
Get-Content .env | Where-Object { $_ -match '^\s*([A-Z_]+)=(.*)$' } | ForEach-Object {
    Set-Item -Path "Env:$($Matches[1])" -Value $Matches[2]
}
$agentName = if ($env:AGENT_NAME) { $env:AGENT_NAME } else { "fact-checker" }
$foundryUserRole = "53ca6127-db72-4b80-b1b0-d745d6d5456d"   # role definition ID (the role was recently renamed)

$endpoint = $env:FOUNDRY_PROJECT_ENDPOINT
$account = ([Uri]$endpoint).Host.Split(".")[0]
$project = $endpoint.TrimEnd("/").Split("/")[-1]
$accountId = az resource list --resource-type Microsoft.CognitiveServices/accounts --name $account --query "[0].id" -o tsv
$projectId = "$accountId/projects/$project"

$principalId = az rest --method GET `
    --url "$endpoint/agents/$agentName`?api-version=v1" `
    --resource "https://ai.azure.com" `
    --query instance_identity.principal_id -o tsv

az role assignment create `
    --assignee-object-id $principalId `
    --assignee-principal-type ServicePrincipal `
    --role $foundryUserRole `
    --scope $projectId `
    --output none

Write-Host "Foundry User assigned to the identity of agent $agentName on project $project."
