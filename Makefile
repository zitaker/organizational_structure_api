.PHONY: help build up up-logs down logs shell test migrate makemigrations createsuperuser

DOCKER_COMPOSE := $(shell docker compose version >/dev/null 2>&1 && echo "docker compose" || echo "docker-compose")

help:
	@echo "Available commands:"
	@echo "  make build          Build Docker images"
	@echo "  make up             Start all services in background"
	@echo "  make up-logs        Start all services and show logs (foreground)"
	@echo "  make down           Stop all services"
	@echo "  make logs           Show logs from all services"
	@echo "  make shell          Open shell in app container"
	@echo "  make test           Run tests in test container"
	@echo "  make migrate        Run database migrations"
	@echo "  make makemigrations Create new migrations"
	@echo "  make createsuperuser Create a superuser for Django admin"

build:
	$(DOCKER_COMPOSE) build

up:
	$(DOCKER_COMPOSE) up -d

up-logs:
	$(DOCKER_COMPOSE) up

down:
	$(DOCKER_COMPOSE) down

logs:
	$(DOCKER_COMPOSE) logs -f

shell:
	$(DOCKER_COMPOSE) exec app /bin/bash

test:
	$(DOCKER_COMPOSE) run --rm test

migrate:
	$(DOCKER_COMPOSE) exec app python manage.py migrate

makemigrations:
	$(DOCKER_COMPOSE) exec app python manage.py makemigrations

createsuperuser:
	$(DOCKER_COMPOSE) exec app python manage.py createsuperuser
