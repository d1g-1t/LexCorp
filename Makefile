.PHONY: setup up down test logs shell migrate lint typecheck help

# ── Docker Compose shorthand ──────────────────────────────────────────────────
COMPOSE      = docker compose
API_SERVICE  = api
COMPOSE_FILE = docker-compose.yml

# Portable copy (Windows GnuWin32 make has no `cp`)
PYTHON       = python

# ── Python / test runner ──────────────────────────────────────────────────────
PYTEST_ARGS  = -v --tb=short --cov=src --cov-report=term-missing --cov-fail-under=80

# =============================================================================
#  Default target
# =============================================================================
help:
	@echo ""
	@echo "  LexCorp - dev commands"
	@echo ""
	@echo "  make setup    - full setup from a fresh clone"
	@echo "  make up       - start the full stack (detached)"
	@echo "  make down     - stop and remove volumes"
	@echo "  make test     - lint + type-check + pytest"
	@echo "  make migrate  - run alembic upgrade head"
	@echo "  make logs     - tail api logs"
	@echo "  make shell    - bash inside the api container"
	@echo ""

# =============================================================================
#  Setup - one command from zero to running app
# =============================================================================
setup: .env
	@echo ">>> Building images and starting services..."
	$(COMPOSE) -f $(COMPOSE_FILE) up -d --build --wait

	@echo ">>> Running Alembic migrations..."
	$(COMPOSE) exec -T $(API_SERVICE) alembic upgrade head

	@echo ""
	@echo "  Done! API: http://localhost:9100/docs"
	@echo "  Grafana:   http://localhost:9000  (admin/admin)"
	@echo "  Flower:    http://localhost:9555"
	@echo ""

.env:
	@echo ">>> .env not found - copying from .env.example"
	$(PYTHON) -c "import shutil; shutil.copyfile('.env.example', '.env')"
	@echo ">>> Review .env and set PASETO_SECRET_KEY + POSTGRES_PASSWORD"

# =============================================================================
#  Docker
# =============================================================================
up:
	$(COMPOSE) -f $(COMPOSE_FILE) up -d --wait

down:
	$(COMPOSE) -f $(COMPOSE_FILE) down -v

restart:
	$(COMPOSE) -f $(COMPOSE_FILE) restart $(API_SERVICE)

# =============================================================================
#  Migrations
# =============================================================================
migrate:
	$(COMPOSE) exec -T $(API_SERVICE) alembic upgrade head

# =============================================================================
#  Tests
# =============================================================================
test: lint typecheck pytest

pytest:
	pytest $(PYTEST_ARGS) tests/

pytest-unit:
	pytest $(PYTEST_ARGS) tests/unit/

pytest-e2e:
	pytest $(PYTEST_ARGS) tests/e2e/

# =============================================================================
#  Code quality
# =============================================================================
lint:
	ruff check src/ tests/

lint-fix:
	ruff check --fix src/ tests/
	ruff format src/ tests/

typecheck:
	mypy src/

format:
	ruff format src/ tests/

# =============================================================================
#  Dev helpers
# =============================================================================
logs:
	$(COMPOSE) logs -f $(API_SERVICE)

logs-worker:
	$(COMPOSE) logs -f worker

shell:
	$(COMPOSE) exec $(API_SERVICE) bash

ps:
	$(COMPOSE) ps

# =============================================================================
#  Ollama model management
# =============================================================================
ollama-pull:
	$(COMPOSE) exec ollama ollama pull llama3

ollama-list:
	$(COMPOSE) exec ollama ollama list
