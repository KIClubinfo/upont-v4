## ~ General
build:
	docker-compose build

build_prod:
	./scripts/build.sh

start:
	docker-compose up -d

start_prod:
	./scripts/start.sh

stop:
	docker-compose stop

stop_prod:
	./scripts/stop.sh