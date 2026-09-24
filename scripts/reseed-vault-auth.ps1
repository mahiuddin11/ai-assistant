$ErrorActionPreference = "Stop"

$VaultContainer = "ai-assistant-vault"
$VaultAddr = "http://127.0.0.1:8200"
$VaultToken = "dev-root-token"
$SecretPath = "secret/auth-service"

$DatabaseUrl = "postgresql+psycopg://root:admin123@localhost:5432/ai_assistant"
$JwtSecret = "dev-super-secret-jwt-key-change-in-prod"

docker exec -e "VAULT_ADDR=$VaultAddr" -e "VAULT_TOKEN=$VaultToken" $VaultContainer `
    vault kv put $SecretPath `
    "DATABASE_URL=$DatabaseUrl" `
    "JWT_SECRET=$JwtSecret"

Write-Host "Vault secrets reseeded successfully for auth-service."