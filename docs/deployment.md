# Deployment

## Local Development
```bash
cp .env.example .env
docker compose up --build
```

To bring up infrastructure dependencies (Postgres, Redis, Qdrant, MinIO, RabbitMQ):
```bash
docker compose --profile infra up
```

## Staging/Production
- Use Kubernetes (see `deploy/k8s/README.md`) or managed services.
- Enable TLS, autoscaling, and secret management (Vault, AWS Secrets Manager).
- Use CI/CD for lint, build, and deployment automation.
