# these will speed up builds, for docker-compose >= 1.25
export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1

TEST_TARGET?=tests/unit/

all: down build up lint test

build: 
	docker-compose -f docker/docker-compose.yml build

up: 
	docker-compose -f docker/docker-compose.yml up -d

restart:
	docker-compose -f docker/docker-compose.yml restart

down:
	docker-compose -f docker/docker-compose.yml down --remove-orphans

lint: 
	poetry run pylint src/**/*.py tests/**/*.py

test: up
	TARGET=tests/unit/
	docker-compose -f docker/docker-compose.yml exec -T app pytest $(TEST_TARGET)

logs:
	docker-compose -f docker/docker-compose.yml logs --tail=25

logf:
	docker-compose -f docker/docker-compose.yml logs -f

exec-bash: up
	docker-compose -f docker/docker-compose.yml exec app bash
