# ======================================================
# Makefile for Django + Docker project
# ======================================================

# Root paths
DOCKER_DIR = infra/docker

# Compose files
COMPOSE_FILES_BASE = -f $(DOCKER_DIR)/docker-compose.base
COMPOSE_FILES_DEV = ${COMPOSE_FILES_BASE} -f $(DOCKER_DIR)/docker-compose.dev
COMPOSE_FILES_TEST = ${COMPOSE_FILES_BASE} -f $(DOCKER_DIR)/docker-compose.test
COMPOSE_FILES_PROD = ${COMPOSE_FILES_BASE} -f $(DOCKER_DIR)/docker-compose.prod

# ======================================================
# HELP
# ======================================================

.PHONY: help
help:
	@echo "📋 Available commands:"
	@echo ""
	@echo "🔧 Django Management:"
	@echo "  make makemigrations    - Create new database migrations"
	@echo "  make migrate           - Apply database migrations"
	@echo "  make createsuperuser   - Create Django superuser"
	@echo ""
	@echo "🚀 Development:"
	@echo "  make dev               - Start development server"
	@echo "  make dev-down          - Stop development server"
	@echo "  make dev-rebuild       - Rebuild development containers"
	@echo "  make dev-seed          - Seed database with test data"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test              - Run tests in Docker"
	@echo "  make test-down         - Stop test containers"
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
# DJANGO MANAGEMENT COMMANDS
# ======================================================

.PHONY: makemigrations
makemigrations:
	@echo "📦 Making new migrations..."
	docker compose $(COMPOSE_FILES_DEV) run --rm backend python manage.py makemigrations

.PHONY: migrate
migrate:
	@echo "⚙️ Applying database migrations..."
	docker compose $(COMPOSE_FILES_DEV) run --rm backend python manage.py migrate

.PHONY: createsuperuser
createsuperuser:
	@echo "👤 Creating Django superuser..."
	docker compose $(COMPOSE_FILES_DEV) run --rm backend python manage.py createsuperuser

# ======================================================
# DEVELOPMENT COMMANDS
# ======================================================

.PHONY: dev
dev:
	@echo "🚀 Starting Django (development mode)..."
	docker compose $(COMPOSE_FILES_DEV) up --build --remove-orphans -d

.PHONY: dev-down
dev-down:
	@echo "🧹 Deleting dev container, networks, and volumes..."
	docker compose $(COMPOSE_FILES_DEV) down

.PHONY: dev-rebuild
dev-rebuild:
	@echo "♻️  Rebuilding development image..."
	docker compose $(COMPOSE_FILES_DEV) up --build --force-recreate --remove-orphans -d

.PHONY: dev-seed
dev-seed:
	@echo "🌱 Seeding database with test data..."
	docker compose $(COMPOSE_FILES_DEV) run --rm backend python manage.py seed_database

# ======================================================
# TEST COMMANDS
# ======================================================

.PHONY: test
test:
	@echo "🧪 Running tests..."
	docker compose $(COMPOSE_FILES_TEST) up --build --abort-on-container-exit --remove-orphans
	@docker compose $(COMPOSE_FILES_TEST) down

.PHONY: test-down
test-down:
	@echo "🧹 Deleting test container, networks, and volumes..."
	docker compose $(COMPOSE_FILES_TEST) down -v

# ======================================================
# PRODUCTION COMMANDS
# ======================================================

.PHONY: prod
prod:
	@echo "🚀 Starting production server (Gunicorn)..."
	docker compose $(COMPOSE_FILES_PROD) up --build --remove-orphans -d

.PHONY: prod-down
prod-down:
	@echo "🧹 Stopping production containers..."
	docker compose $(COMPOSE_FILES_PROD) down

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
	pip-audit -r requirements/dev.txt

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

# ======================================================
# DEPENDENCIES & INITIALIZATION COMMANDS
# ======================================================

.PHONY: setup
setup: pip-install-dev
	@echo "🚀 Installing pre-commit hooks..."
	pre-commit install --hook-type pre-commit

.PHONY: pip-uninstall
pip-uninstall:
	@echo "🧹 Uninstall all libraries..."
	pip freeze | xargs pip uninstall -y

.PHONY: pip-install-dev
pip-install-dev:
	@echo "✅ Install all libraries..."
	pip install -r requirements/dev.txt

.PHONY: pip-install-test
pip-install-test: 
	@echo "✅ Install all libraries..."
	pip install -r requirements/test.txt

.PHONY: pip-install-prod
pip-install-prod:
	@echo "✅ Install all libraries..."
	pip install -r requirements/prod.txt
