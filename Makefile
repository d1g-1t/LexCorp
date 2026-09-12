.PHONY: setup up down test install logs shell migrate lint typecheck help

# ── Docker Compose shorthand ──────────────────────────────────────────────────
COMPOSE      = docker compose
API_SERVICE  = api
COMPOSE_FILE = docker-compose.yml

# Portable Python: prefer local .venv (Windows Scripts / Unix bin)
ifeq ($(OS),Windows_NT)
  VENV_PYTHON = .venv/Scripts/python.exe
else
  VENV_PYTHON = .venv/bin/python
endif

ifneq ($(wildcard $(VENV_PYTHON)),)
  PYTHON = $(VENV_PYTHON)
else
  PYTHON = python
endif

# ── Python / test runner ──────────────────────────────────────────────────────
PYTEST_ARGS  = -v --tb=short --cov=src --cov-report=term-missing --cov-fail-under=60

# =============================================================================
#  Default target
# =============================================================================
help:
	@echo ""
	@echo "  LexCorp - dev commands"
	@echo ""
	@echo "  make setup      - full setup from a fresh clone (Docker)"
	@echo "  make install    - local .venv + pip install -e .[dev]"
	@echo "  make test       - pytest (needs make install)"
	@echo "  make check      - lint + type-check + pytest"
	@echo "  make pytest     - pytest only"
	@echo "  make up         - start the full stack (detached)"
	@echo "  make down       - stop and remove volumes"
	@echo "  make migrate    - run alembic upgrade head"
	@echo "  make logs       - tail api logs"
	@echo "  make shell      - bash inside the api container"
	@echo ""

# =============================================================================
#  Local Python toolchain
# =============================================================================
install:
	@echo ">>> Creating .venv and installing project + dev deps..."
	python scripts/bootstrap_dev.py

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
	python -c "import shutil; shutil.copyfile('.env.example', '.env')"
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
# `make test` runs the suite. Full quality gate: `make check`
test: pytest

check: lint typecheck pytest

pytest:
	$(PYTHON) -m pytest $(PYTEST_ARGS) tests/

pytest-unit:
	$(PYTHON) -m pytest $(PYTEST_ARGS) tests/unit/

pytest-e2e:
	$(PYTHON) -m pytest $(PYTEST_ARGS) tests/e2e/

# =============================================================================
#  Code quality
# =============================================================================
lint:
	$(PYTHON) -m ruff check src/ tests/

lint-fix:
	$(PYTHON) -m ruff check --fix src/ tests/
	$(PYTHON) -m ruff format src/ tests/

typecheck:
	$(PYTHON) -m mypy src/

format:
	$(PYTHON) -m ruff format src/ tests/

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
