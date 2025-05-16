.PHONY: start
start: ## cria ambiente virtual com poetry e instala bibliotecas de dev
	git init 
	poetry init -n
	poetry add --group dev black
	poetry add --group dev isort
	poetry add --group dev pytest
	poetry add --group dev pytest-cov
	poetry add --group dev pytest-rerunfailures
	poetry add --group dev ipython:8.15
	poetry add --group dev python-dotenv
	mkdir tests 
	type NUL > tests/__init__.py
	echo __pycache__/ > .gitignore
	echo .env >> .gitignore
	echo htmlcov/ >> .gitignore
	echo .coverage >> .gitignore
	echo .pytest_cache/ >> .gitignore
	poetry add --group doc mkdocs-material pyyaml@6.0
	poetry add --group doc mkdocstrings
	poetry add --group doc mkdocstrings-python
	poetry run mkdocs new .
	mkdir code
	type NUL > code/__init__.py



.PHONY: docs
docs:
	poetry run mkdocs serve

.PHONY: down
down:
	docker compose down

.PHONY: format
format: ## formata o script e ordena os imports
	poetry run black .
	poetry run isort .

.PHONY: logs
logs: 
	docker compose logs --follow

.PHONY: mark-test
mark-test: # make mark-test m=email
	poetry run pytest . -x -s --cov=code -vv -m ${m}
	poetry run coverage html

.PHONY: push
push:
	@make test
	git push -u origin main

.PHONY: requirements
requirements:
	poetry export -o requirements.txt --without-hashes --with dev

.PHONY: test
test: 
	poetry run pytest . -x -s --cov=code -vv
	poetry run coverage html

.PHONY: up
up: 
	docker compose down
	docker compose up -d

.PHONY: ipython
ipython:
	powershell -Command "$$env:PYTHONPATH = (Get-Location).Path; poetry run ipython -i ${file}"

.PHONY: run
run: 
	poetry run fastapi dev code/app.py