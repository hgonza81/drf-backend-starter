# ======================================================
# Makefile for Django + Docker project
# ======================================================

# Root paths
DOCKER_DIR = infra/docker

# Compose files
COMPOSE_FILES_BASE = -f $(DOCKER_DIR)/docker-compose.base
COMPOSE_FILES_DEV = ${COMPOSE_FILES_BASE} -f $(DOCKER_DIR)/docker-compose.dev
COMPOSE_FILES_TEST_CI = ${COMPOSE_FILES_BASE} -f $(DOCKER_DIR)/docker-compose.test-ci

# ======================================================
# HELP
# ======================================================

.PHONY: help
help:
	@echo "📋 Available commands:"
	@echo ""
	@echo "🚀 Development:"
	@echo "  make dev               - Start development server"
	@echo "  make dev-down          - Stop development server"
	@echo "  make dev-rebuild       - Rebuild development containers"
	@echo "  make dev-seed          - Seed database with test data"
	@echo ""
	@echo "🔧 Django Management:"
	@echo "  make makemigrations    - Create new database migrations"
	@echo "  make migrate           - Apply database migrations"
	@echo "  make createsuperuser   - Create Django superuser"
	@echo ""	
	@echo "🧪 Local Testing:"
	@echo "  make test              - Start test container in detached mode"
	@echo "  make test-migrate      - Apply database migrations"
	@echo "  make test-run          - Run tests without coverage (use CMD=<test> for specific tests)"
	@echo "  make test-run-cov      - Run tests with coverage report (use CMD=<test> for specific tests)"
	@echo "  make test-rebuild      - Rebuild test containers from scratch"
	@echo "  make test-down         - Stop test containers and clean up"
	@echo ""	
	@echo "🧪 CI Testing:"
	@echo "  make tests-ci          - Run tests in Docker for CI workflow"
	@echo ""
	@echo "🚢 Production:"
	@echo "  make prod              - Start production server"
	@echo "  make prod-down         - Stop production server"
	@echo ""
	@echo "✅ Code Quality:"
	@echo "  make lint              - Run Ruff linter & formatter (auto-fix)"
	@echo "  make lint-check        - Run Ruff lint check (no fixes)"
	@echo "  make hooks-check     - Validate configuration files"
	@echo "  make detect-secrets    - Detect secrets in codebase"
	@echo "  make security-check    - Run Bandit security scan & pip-audit"
	@echo "  make quality-checks    - Run all quality checks (summary)"
	@echo ""
	@echo "📦 Dependencies:"
	@echo "  make setup             - Install pre-commit hooks"
	@echo "  make pip-uninstall     - Uninstall all libraries"
	@echo "  make pip-install-dev   - Install dev dependencies"
	@echo "  make pip-install-test  - Install test dependencies"
	@echo "  make pip-install-prod  - Install prod dependencies"
	@echo ""

# ======================================================
# DEPENDENCIES & DEV ENVIRONMENT SETUP COMMANDS
# ======================================================

.PHONY: pip-install
pip-install-dev:
	@echo "✅ Install all libraries..."
	pip install -r requirements/dev.txt

.PHONY: setup
setup: pip-install
	@echo "🚀 Installing all libraries and Git hooks..."
	pre-commit install --hook-type pre-commit

.PHONY: pip-uninstall
pip-uninstall:
	@echo "🧹 Uninstall all libraries..."
	pip freeze | xargs pip uninstall -y
	
# ======================================================
# DEVELOPMENT COMMANDS
# ======================================================

.PHONY: up
up:
	@echo "🚀 Starting Django (dev container)..."
	docker compose $(COMPOSE_FILES_DEV) up -d

.PHONY: test
test: up
	@echo "🚀 Running tests (dev container)..."
	docker compose $(COMPOSE_FILES_DEV) exec backend pytest -vv --no-cov $(CMD)

.PHONY: test-cov
test-cov: up
	@echo "🚀 Running tests in dev container (with coverage)..."
	docker compose $(COMPOSE_FILES_DEV) exec backend pytest $(CMD)

.PHONY: seed
seed: up
	@echo "🌱 Seeding database with test data (dev container)..."
	docker compose $(COMPOSE_FILES_DEV) exec backend python manage.py seed_database

.PHONY: rebuild
rebuild:
	@set -e; \
	echo "🔄 Rebuilding (dev container)..."; \
	docker compose $(COMPOSE_FILES_DEV) up --build --force-recreate -d; \
	echo "🧹 Cleaning up dangling images..."; \
	docker image prune -f > /dev/null; \
	echo "✅ Dev container rebuilt and cleaned successfully."

.PHONY: down
down:
	@echo "🧹 Deleting dev container, networks, and volumes..."
	docker compose $(COMPOSE_FILES_DEV) down

# ======================================================
# DJANGO MANAGEMENT COMMANDS
# ======================================================

.PHONY: makemigrations
makemigrations: up
	@echo "📦 Making new migrations (dev container)..."
	docker compose $(COMPOSE_FILES_DEV) exec backend python manage.py makemigrations

.PHONY: migrate
migrate: up
	@echo "⚙️ Applying database migrations (dev container)..."
	docker compose $(COMPOSE_FILES_DEV) exec backend python manage.py migrate

.PHONY: createsuperuser
createsuperuser: up
	@echo "👤 Creating Django superuser (dev container)..."
	docker compose $(COMPOSE_FILES_DEV) exec backend python manage.py createsuperuser

# ======================================================
# CI WORKFLOW TEST COMMANDS
# ======================================================

.PHONE: tests-ci
tests-ci:
	@echo "🧪 Running tests (test container)..."
	docker compose $(COMPOSE_FILES_TEST_CI) up \
		--build \
		--abort-on-container-exit \
		--exit-code-from backend \
		--remove-orphans

# ======================================================
# CODE QUALITY & VALIDATION COMMANDS
# ======================================================

.PHONY: lint
lint:
	@echo "🧹 Running Ruff linter & formatter (auto-fix)..."
	ruff format && ruff check --fix

.PHONY: lint-check
lint-check:
	@echo "🔍 Running Ruff lint check (no fixes)..."
	ruff check

.PHONY: hooks-check
hooks-check:
	@echo "🧩 Running official pre-commit hooks (YAML, TOML, big files, etc.)..."
	@bash -c "pre-commit run check-yaml --all-files || true"
	@bash -c "pre-commit run check-toml --all-files || true"
	@bash -c "pre-commit run check-added-large-files --all-files || true"
	@bash -c "pre-commit run check-merge-conflict --all-files || true"

.PHONY: detect-secrets
detect-secrets:
	@echo "🔐 Detecting secrets in codebase..."
	@if [ -f .secrets.baseline ]; then \
		detect-secrets-hook --baseline .secrets.baseline $$(git ls-files); \
	else \
		detect-secrets-hook $$(git ls-files); \
	fi
	@echo "🔐 Finished secrets in codebase."

.PHONY: security-check
security-check:
	@echo "🔒 Running Bandit security scan..."
	bandit -r ./app -c pyproject.toml
	@echo "🛡️  Running Pip-audit for dependency vulnerabilities..."
	pip-audit -r requirements/base.txt -r requirements/dev.txt -r requirements/test-ci.txt -r requirements/prod.txt

.PHONY: quality-checks
quality-checks:
	@echo "🔍 Running code quality checks..."
	@echo ""
	@printf "  Lint check...................... "
	@make lint-check > /dev/null 2>&1 && echo "✅ PASSED" || echo "❌ FAILED"
	@printf "  Pre-commit hooks validations.... "
	@make hooks-check > /dev/null 2>&1 && echo "✅ PASSED" || echo "❌ FAILED"
	@printf "  Detect secrets.................. "
	@make detect-secrets > /dev/null 2>&1 && echo "✅ PASSED" || echo "❌ FAILED"
	@printf "  Security scan (Bandit + Audit).. "
	@make security-check > /dev/null 2>&1 && echo "✅ PASSED" || echo "❌ FAILED"
	@echo ""
	@echo "✅ All quality checks completed"

