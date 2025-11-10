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
# DJANGO MANAGEMENT COMMANDS
# ======================================================

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
# DEV COMMANDS
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
# PROD COMMANDS
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
