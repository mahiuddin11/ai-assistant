# Infrastructure

এই ফোল্ডারে ডিপ্লয়মেন্ট ও ইনফ্রাস্ট্রাকচার কনফিগারেশন থাকবে   — Dockerfile, Helm chart, Kubernetes manifest, CI/CD পাইপলাইন ডেফিনিশন।

## Local Development Services

| Service | Container Name | Port | Purpose |
|---|---|---|---|
| PostgreSQL 16 | `ai-assistant-postgres` | 5432 | Primary relational database |
| NATS | `ai-assistant-nats` | 4222 (client), 8222 (monitoring) | Event bus |
| Vault (dev mode) | `ai-assistant-vault` | 8200 | Secrets management (dev mode — not for staging/prod) |


| Hello-world Service | `ai-assistant-hello-world` | 8000 | Foundation dummy service |

### Starting all services

```powershell
docker start ai-assistant-postgres ai-assistant-nats ai-assistant-vault
```

⚠️ Vault is running in **dev mode** (`VAULT_DEV_ROOT_TOKEN_ID`) — this is unsealed automatically and stores nothing persistently. This is acceptable for local development only. Staging/production Vault setup will require a proper unseal/storage configuration.