ifneq ("$(wildcard .env)","")
	include .env
	export
endif

# --- Configuration ---
COMPOSE = docker compose
BACKEND_SVC = $(PROJECT_NAME)_backend
CELERY_SVC = $(PROJECT_NAME)_celery
FLOWER_SVC = $(PROJECT_NAME)_flower
EXEC = docker exec -it $(BACKEND_SVC)
PYTHON = $(EXEC) python manage.py
TAIL_LOGS = 50
TEST_WORKERS = auto

.DEFAULT_GOAL := up-logs

# --- System ---
.PHONY: help prepare-env clean-images remove-containers

help: ## Show this help message
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

prepare-env: ## Create .env from template
	@test -f .env || cp .env-dist .env

clean-images: ## Remove all project images
	@if [ -n "$(shell docker images -qa)" ]; then docker rmi $(shell docker images -qa) --force; fi

remove-containers: ## Remove all project containers
	@if [ -n "$(shell docker ps -qa)" ]; then docker rm $(shell docker ps -qa); fi

# --- Docker Orchestration ---
up-logs: up logs

up: create-network prepare-env ## Start containers in background
	@$(COMPOSE) up --force-recreate -d --remove-orphans

down: ## Stop and remove containers
	@$(COMPOSE) down

restart: ## Restart containers
	@$(COMPOSE) restart

build: create-network prepare-env ## Build images
	@$(COMPOSE) build

down-up: down up-logs ## Recreate services

complete-build: build down-up ## Full rebuild cycle

complete-build-dev: build down-up install-dev-dependencies ## Full rebuild cycle with dev dependencies

prod-up: create-network
	@$(COMPOSE) -f compose.yml up -d --build --remove-orphans

# --- Development & Logs ---
.PHONY: logs celery-logs flower-logs all-logs bash shell

logs: ## Show backend logs
	@docker logs --tail $(TAIL_LOGS) -f $(BACKEND_SVC)

celery-logs: ## Show celery logs
	@docker logs --tail $(TAIL_LOGS) -f $(CELERY_SVC)

flower-logs: ## Show flower logs
	@docker logs --tail $(TAIL_LOGS) -f $(FLOWER_SVC)

all-logs: ## Show all services logs
	@$(COMPOSE) logs --tail $(TAIL_LOGS) -f

bash: ## Access backend bash
	@$(EXEC) bash

shell: ## Access Django shell_plus
	@$(PYTHON) shell_plus

# --- Database & Migrations ---
.PHONY: make-migrations migrate migrations messages

make-migrations: ## Create new migrations
	@$(PYTHON) makemigrations

migrate: ## Run migrations
	@$(PYTHON) migrate $(ARGS)

migrations: make-migrations migrate ## Create and run migrations

messages: ## Extract and compile translations
	@$(PYTHON) makemessages -l es -a -i *.txt
	@$(PYTHON) compilemessages -v 3

# --- Quality Assurance & Testing ---
.PHONY: test fast-test test-recreate install-dev-dependencies clean-coverage coverage-report coverage-combine

install-dev-dependencies: ## Sync dev dependencies
	@$(EXEC) uv sync --extra dev

clean-coverage: ## Clean previous coverage results
	@$(EXEC) rm -f .coverage coverage.xml
	@$(EXEC) rm -f .coverage.*

coverage-combine: ## Merge coverage files from parallel execution
	@$(EXEC) uv run coverage combine || true

coverage-report: coverage-combine ## Generate XML and console coverage reports
	@$(EXEC) uv run coverage xml
	@$(EXEC) uv run coverage report

test: clean-coverage install-dev-dependencies ## Run tests
	@$(EXEC) uv run coverage run manage.py test --parallel=$(TEST_WORKERS) --keepdb
	@$(MAKE) coverage-report

fast-test: clean-coverage ## Run tests with failfast
	@$(EXEC) uv run coverage run manage.py test --parallel=$(TEST_WORKERS) --keepdb --failfast
	@$(MAKE) coverage-report

test-recreate: install-dev-dependencies ## Run tests recreating database
	@$(EXEC) uv run coverage run manage.py test --parallel=$(TEST_WORKERS) --noinput
	@$(MAKE) coverage-report

create-network: ## Create shared network if not exists
	@docker network inspect ideological_global_network >/dev/null 2>&1 || docker network create ideological_global_network
