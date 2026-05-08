# Contributing

## Development Setup
1. Install Node.js and Python 3.11+.
2. Run `npm install` in `frontend/`.
3. Run `pip install -r services/requirements.txt`.

## Local Services
```bash
cp .env.example .env
docker compose up --build
```

## Code Standards
- Keep services isolated to their bounded context.
- Use OpenAPI descriptions for endpoints.
- Add tests for new workflows where possible.
