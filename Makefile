.PHONY: clean clean-test clean-pyc clean-build help install build lint typecheck test app coverage
.DEFAULT_GOAL := help

UV=uv

build: install test lint typecheck

install:
	$(UV) sync --group dev

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
	rm -fr coverage_html_report
	rm -fr .ruff_cache
	rm -fr .mypy_cache
	rm -fr .ty_cache

lint: ## run ruff linter
	$(UV) run ruff check src/ tests/

typecheck: ## run ty type checker
	$(UV) run ty check src/

test: ## run tests with coverage
	$(UV) run python -m pytest --cov=fastapi_todos tests/ --print

app: ## run the API with auto-reload
	$(UV) run uvicorn fastapi_todos.main:app --reload --app-dir src

coverage: ## write HTML coverage report
	$(UV) run python -m pytest --cov=fastapi_todos --cov-report=html:coverage_html_report tests/
	@echo "Open coverage_html_report/index.html"
