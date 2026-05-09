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

### LaTeX Rendering
Install `texlive-latex-base` (or equivalent) in the resume-service runtime if you want PDF outputs from LaTeX templates.

## Staging/Production
- Use Kubernetes (see `deploy/k8s/README.md`) or managed services.
- Enable TLS, autoscaling, and secret management (Vault, AWS Secrets Manager).
- Use CI/CD for lint, build, and deployment automation.
