$ErrorActionPreference = "Stop"

$VaultContainer = "ai-assistant-vault"
$VaultAddr = "http://127.0.0.1:8200"
$VaultToken = "dev-root-token"
$SecretPath = "secret/conversation-service"
$LocalSecretsFile = Join-Path $PSScriptRoot "..\.env.vault.local"

if (-not (Test-Path $LocalSecretsFile)) {
    Write-Host "Local secrets file not found: $LocalSecretsFile"
    exit 1
}

Get-Content $LocalSecretsFile | ForEach-Object {
    if ($_ -match '^\s*([^#=]+?)\s*=\s*(.*)\s*$') {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim()

        if ($value) {
            Set-Item -Path "Env:$name" -Value $value
        }
    }
}

if (-not $env:GEMINI_API_KEY) {
    Write-Host "GEMINI_API_KEY is missing from .env.vault.local"
    exit 1
}

if (-not $env:ANTHROPIC_API_KEY) {
    Write-Host "ANTHROPIC_API_KEY is missing from .env.vault.local"
    exit 1
}

$DatabaseUrl = "postgresql+psycopg://root:admin123@localhost:5432/ai_assistant"
$RedisUrl = "redis://localhost:6379/0"
$QdrantUrl = "http://localhost:6333"

docker exec -e "VAULT_ADDR=$VaultAddr" -e "VAULT_TOKEN=$VaultToken" $VaultContainer `
    vault kv put $SecretPath `
    "DATABASE_URL=$DatabaseUrl" `
    "GEMINI_API_KEY=$env:GEMINI_API_KEY" `
    "ANTHROPIC_API_KEY=$env:ANTHROPIC_API_KEY" `
    "REDIS_URL=$RedisUrl" `
    "QDRANT_URL=$QdrantUrl"

Write-Host "Vault secrets reseeded successfully."