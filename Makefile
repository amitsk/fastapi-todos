.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

PDM=pdm

build: install test lint

install: 
	$(PDM) install -d

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint: ## check style with flake8
	$(PDM) run pyflakes fastapi_todos/ tests
	$(PDM)  run mypy  fastapi_todos/
	$(PDM)  run pytype  fastapi_todos/

pytype:
	$(PDM)  -d import-error fastapi_todos/

mypy:
	$(PDM)   --namespace-packages fastapi_todos/


test: ## run tests quickly with the default Python
	$(PDM)  run test

app:
	$(PDM) run app

coverage: ## check code coverage quickly with the default Python
	coverage run --source {{ cookiecutter.project_module }} -m pytest
	coverage report -m
	coverage html


