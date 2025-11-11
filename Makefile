# ======================================================
# Makefile for Django + Docker project
# ======================================================

# Root paths
DOCKER_DIR=infra/docker
ENVS_DIR=envs

# Environment files
ENV_BASE=$(ENVS_DIR)/.env.base
ENV_DEV=$(ENVS_DIR)/.env.dev
ENV_TEST=$(ENVS_DIR)/.env.test
ENV_PROD=$(ENVS_DIR)/.env.prod

# Compose files
COMPOSE_BASE=$(DOCKER_DIR)/docker-compose.base
COMPOSE_DEV=$(DOCKER_DIR)/docker-compose.dev
COMPOSE_TEST=$(DOCKER_DIR)/docker-compose.test
COMPOSE_PROD=$(DOCKER_DIR)/docker-compose.prod

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
	@echo "✅ Code Quality:"
	@echo "  make lint              - Run Ruff linter & formatter (auto-fix)"
	@echo "  make lint-check        - Run Ruff lint check (no fixes)"
	@echo "  make type-check        - Run Mypy type checks"
	@echo "  make detect-secrets    - Detect secrets in codebase"
	@echo "  make security-check    - Run Bandit security scan & pip-audit"
	@echo "  make configs-check     - Validate configuration files"
	@echo "  make quality-checks    - Run all quality checks (summary)"
	@echo ""
	@echo "🐳 CI Commands:"
	@echo "  make ci-lint           - Run lint in Docker (for CI)"
	@echo "  make ci-type-check     - Run type check in Docker (for CI)"
	@echo ""
	@echo "📦 Dependencies:"
	@echo "  make setup             - Install pre-commit hooks"
	@echo "  make pip-freeze        - Freeze dependencies to requirements/base.txt"
	@echo "  make pip-uninstall     - Uninstall all libraries"
	@echo "  make pip-install-dev   - Install dev dependencies"
	@echo "  make pip-install-test  - Install test dependencies"
	@echo "  make pip-install-prod  - Install prod dependencies"
	@echo ""
	@echo "🚢 Production:"
	@echo "  make prod              - Start production server"
	@echo "  make prod-down         - Stop production server"

# ======================================================
# DJANGO MANAGEMENT COMMANDS
# ============

.PHONY: makemigrations, 
makemigrations:
	@echo "📦 Making new migrations..."
	python manage.py makemigrations

.PHONY: migrate
migrate:
	@echo "⚙️ Applying database migrations..."
	python manage.py migrate

.PHONY: createsuperuser
createsuperuser:
	@echo "👤 Creating Django superuser..."
	python manage.py createsuperuser

# ======================================================
# DEVELOPMENT COMMANDS
# ======================================================

.PHONY: dev
dev:
	@echo "🚀 Starting Django (development mode)..."
	@export $$(grep -hv '^#' $(ENV_BASE) $(ENV_DEV) | grep . | xargs) && \
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_DEV) up --build -d

.PHONY: dev-down
dev-down:
	@echo "🧹 Deleting dev container, networks, and volumes..."
	@export $$(grep -hv '^#' $(ENV_BASE) $(ENV_DEV) | grep . | xargs) && \
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_DEV) down

.PHONY: dev-rebuild
dev-rebuild:
	@echo "♻️  Rebuilding development image..."
	@export $$(grep -hv '^#' $(ENV_BASE) $(ENV_DEV) | grep . | xargs) && \
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_DEV) up --build --force-recreate -d

.PHONY: dev-seed
dev-seed: dev
	docker exec backend_dev python manage.py seed_database

# ======================================================
# TEST COMMANDS
# ======================================================

.PHONY: test
test:
	@echo "🧪 Running tests..."
	@export $$(grep -hv '^#' $(ENV_BASE) $(ENV_TEST) | grep . | xargs) && \
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_TEST) up --build --abort-on-container-exit

.PHONY: test-down
test-down:
	@echo "🧹 Deleting test container, networks, and volumes..."
	@export $$(grep -hv '^#' $(ENV_BASE) $(ENV_TEST) | grep . | xargs) && \
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_TEST) down -v

# ======================================================
# CODE QUALITY & VALIDATION COMMANDS
# ======================================================

.PHONY: lint
lint:
	@echo "🧹 Running Ruff linter & formatter (auto-fix)..."
	ruff check --fix && ruff format

.PHONY: lint-check
lint-check:
	@echo "🔍 Running Ruff lint check (no fixes)..."
	ruff check

.PHONY: type-check
type-check:
	@echo "🔍 Running Mypy type checks..."
	mypy --config-file pyproject.toml

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
	@printf "  Type check...................... "
	@make type-check > /dev/null 2>&1 && echo "✅ PASSED" || echo "❌ FAILED"
	@printf "  Pre-commit hooks validations.... "
	@make hooks-check > /dev/null 2>&1 && echo "✅ PASSED" || echo "❌ FAILED"
	@printf "  Detect secrets.................. "
	@make detect-secrets > /dev/null 2>&1 && echo "✅ PASSED" || echo "❌ FAILED"
	@printf "  Security scan (Bandit + Audit).. "
	@make security-check > /dev/null 2>&1 && echo "✅ PASSED" || echo "❌ FAILED"
	@echo ""
	@echo "✅ All quality checks completed"

# ======================================================
# PRODUCTION COMMANDS
# ======================================================

.PHONY: prod
prod:
	@echo "🚀 Starting production server (Gunicorn)..."
	@export $$(grep -hv '^#' $(ENV_BASE) $(ENV_PROD) | grep . | xargs) && \
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_PROD) up --build -d

.PHONY: prod-down
prod-down:
	@echo "🧹 Stopping production containers..."
	@export $$(grep -hv '^#' $(ENV_BASE) $(ENV_PROD) | grep . | xargs) && \
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_PROD) down

# ======================================================
# REQUIREMENTS & INITIALIZATION COMMANDS
# ======================================================

.PHONY: setup
setup: pip-install-dev
	@echo "🚀 Installing pre-commit hooks..."
	pre-commit install --hook-type pre-commit --hook-type pre-push

.PHONY: freeze
pip-freeze:
	@echo "❄️  Freezing current dependencies to requirements/base.txt..."
	pip freeze > requirements/temp_env_file.txt
	@echo "✅ Dependencies exported successfully!"

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
