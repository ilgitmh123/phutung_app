# Parts Store (Python-only, Docker)

## Quickstart
```bash
cp infra/env/.env.example .env
cd infra && docker compose up -d --build
cd ../backend && python manage.py migrate && python manage.py createsuperuser
# Swagger: http://localhost:8000/api/docs/
```

## Import JSON
```bash
docker compose -f infra/docker-compose.yml exec backend python manage.py import_json /data/parts.json --mode upsert --dry-run
```

## API Upload JSON (admin)
POST http://localhost:8000/api/import/json  (body = JSON object keyed by SKU)
