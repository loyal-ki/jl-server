DOCKER_EXEC = docker exec
DOCKER_COMPOSE = docker compose
RUNNER = journey-lingua-runner
API = journey-lingua-api

.PHONY: initialize
initialize: install-lefthook poetry-install alembic-migration seed

.PHONY: install-lefthook
install-lefthook:
	brew install lefthook
	lefthook install

.PHONY: poetry-install
poetry-install: runner
	$(DOCKER_COMPOSE) exec -T $(RUNNER) bash -c 'poetry install'

.PHONY: build
build:
	$(DOCKER_COMPOSE) build $(API)

.PHONY: build-runner
build-runner:
	$(DOCKER_COMPOSE) build $(RUNNER)

.PHONY: up-api
up-api: 
	$(DOCKER_COMPOSE) up --build -d $(API)
	$(DOCKER_COMPOSE) restart $(API)

.PHONY: up
up: up-api

.PHONY: up-if-not-running
up-if-not-running:
	$(DOCKER_COMPOSE) ps -a --services --status running | grep $(API) || make up


.PHONY: runner
runner:
	$(DOCKER_COMPOSE) ps -a --services --status running | grep $(RUNNER) || $(DOCKER_COMPOSE) up -d $(RUNNER)


.PHONY: alembic-revisions
alembic-revisions: runner
	$(DOCKER_COMPOSE) exec $(RUNNER) bash -c 'cd /app/app/db && alembic revision --autogenerate'

.PHONY: alembic-migration
alembic-migration: runner
	$(DOCKER_COMPOSE) exec $(RUNNER) bash -c 'cd /app/app/db && alembic upgrade head'

.PHONY: alembic-downgrade
alembic-downgrade: runner
	$(DOCKER_COMPOSE) exec $(RUNNER) bash -c 'cd /app/app/db && alembic downgrade -1'

.PHONY: database
database: runner
	$(DOCKER_EXEC) -it journey-lingua-mysql mysql -uroot -p

.PHONY: start
start:
	$(eval include .env)
	$(eval export $(sh sed 's/=.*//' .env))

	poetry run python app/journey_lingua.py

.PHONY: seed
seed: up-if-not-running
	$(DOCKER_COMPOSE) exec -w /app $(API) python /app/app/db/seeds/run.py

.PHONY: test
test:
	$(DOCKER_COMPOSE) run -T journey-lingua-runner pytest --junitxml=pytest.xml --cov-report=term-missing:skip-covered --cov=app tests/ | tee pytest-coverage.txt