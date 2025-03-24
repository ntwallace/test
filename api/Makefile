build-image:
	docker build -t powerx-api -f Dockerfile .

dev-up:
	docker compose -f docker-compose.yml --env-file ./envs/.env.dev up --build -d

seed-db:
	docker compose -f docker-compose.yml --env-file ./envs/.env.dev run app bash -c "python -m scripts.seed"

dev-down:
	docker compose -f docker-compose.yml down

run-pytest:
	docker compose -f docker-compose.testing.yml --env-file ./envs/.env.testing run --rm --build app bash -c "alembic upgrade head && pytest -vv"

build-quality-checker-image:
	docker build -t powerx-api-quality-checker -f Dockerfile.testing .

run-ruff:
	docker run --rm -v ./:/app -it powerx-api-quality-checker python -m ruff check app/ scripts/

run-mypy:
	docker run --rm -v ./:/app -it powerx-api-quality-checker python -m mypy app/ scripts/
