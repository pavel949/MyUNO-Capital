# =============================================================================
# MyUNO Capital — Makefile
# -----------------------------------------------------------------------------
# Thin wrappers around docker compose for the local development stack.
# Service names match docker-compose.yml: frontend, backend, worker,
# postgres, redis, minio.
#
# Run `make` or `make help` to see all available targets.
# =============================================================================

# Use docker compose v2 (the plugin form). Override with: make COMPOSE="docker-compose"
COMPOSE ?= docker compose

.DEFAULT_GOAL := help

.PHONY: help up down build logs migrate makemigration seed test \
        lint format shell psql clean

help: ## Show this help message
	@echo "MyUNO Capital — available make targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'
	@echo ""

up: ## Start all services in the background
	$(COMPOSE) up -d

down: ## Stop all services (keeps volumes/data)
	$(COMPOSE) down

build: ## Build (or rebuild) all service images
	$(COMPOSE) build

logs: ## Tail logs from all services (Ctrl-C to stop)
	$(COMPOSE) logs -f

migrate: ## Apply database migrations (alembic upgrade head)
	$(COMPOSE) exec backend alembic upgrade head

makemigration: ## Create a new migration; pass m="message"
	$(COMPOSE) exec backend alembic revision --autogenerate -m "$(m)"

seed: ## Load seed/demo data into the database
	$(COMPOSE) exec backend python -m app.scripts.seed

test: ## Run backend (pytest) and frontend test suites
	$(COMPOSE) exec backend pytest
	$(COMPOSE) exec frontend npm test

lint: ## Lint backend (ruff) and frontend (eslint)
	$(COMPOSE) exec backend ruff check .
	$(COMPOSE) exec frontend npm run lint

format: ## Auto-format backend (black + ruff) and frontend (prettier)
	$(COMPOSE) exec backend black .
	$(COMPOSE) exec backend ruff format .
	$(COMPOSE) exec frontend npm run format

shell: ## Open a bash shell in the backend container
	$(COMPOSE) exec backend bash

psql: ## Open a psql session against the postgres database
	$(COMPOSE) exec postgres psql -U $${POSTGRES_USER:-myuno} -d $${POSTGRES_DB:-myuno_capital}

clean: ## Stop services AND remove volumes (DESTROYS local data)
	$(COMPOSE) down -v
