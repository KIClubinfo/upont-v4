## ~ General
build:
	docker-compose build

build-prod:
	./scripts/build.sh

start:
	docker-compose up -d

start-prod:
	./scripts/start.sh

stop:
	docker-compose stop

stop-prod:
	./scripts/stop.sh

install: install-pre-commit install-linters

install-pre-commit:
	pip install pre-commit
	pre-commit install

install-linters: install-linters-back install-linters-front

lint: lint-back lint-front

format: format-back format-front

##
## ~ Backend
install-linters-back:
	pip install black flake8

lint-back:
	black back/ --check
	flake8 back/ --config .github/linters/.flake8

format-back:
	black back/

##
## ~ Frontend
install-linters-front:
	npm i eslint eslint-config-prettier eslint-config-airbnb @babel/eslint-parser @typescript-eslint/parser @typescript-eslint/eslint-plugin typescript prettier eslint-plugin-import eslint-plugin-react


lint-front:
	npx prettier --check react/src
	npx eslint react/src

format-front:
	npx prettier --write react/src