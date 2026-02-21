COMPOSE = docker compose -f infra/docker-compose.yml

all: build

up:
	$(COMPOSE) up

down:
	$(COMPOSE) down

restart:
	$(COMPOSE) down
	$(COMPOSE) up

build:
	$(COMPOSE) up --build

logs:
	$(COMPOSE) logs -f

backend:
	docker exec -it hackathon_backend sh

db:
	docker exec -it hackathon_db psql -U app app

reset:
	$(COMPOSE) down -v
	rm -rf infra/db_data

prune:
	docker system prune -f