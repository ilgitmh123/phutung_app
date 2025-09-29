.PHONY: dev-up migrate createsuper seed import-json

dev-up:
	cd infra && docker compose up -d --build
migrate:
	docker compose -f infra/docker-compose.yml exec backend python manage.py migrate
createsuper:
	docker compose -f infra/docker-compose.yml exec backend python manage.py createsuperuser
seed:
	docker compose -f infra/docker-compose.yml exec backend python manage.py loaddata seed.json
import-json:
	docker compose -f infra/docker-compose.yml exec backend python manage.py import_json /data/parts.json --mode upsert
