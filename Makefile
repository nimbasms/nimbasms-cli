.PHONY: help install test lint build release-patch release-minor release-major clean

help: ## Display this help message
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@awk -F ':|##' '/^[^\t].+?:.*?##/ { printf "  %-20s %s\n", $$1, $$NF }' $(MAKEFILE_LIST)

install: ## Install dependencies
	poetry install

test: ## Run tests
	poetry run pytest

lint: ## Run linting checks
	poetry run black .
	poetry run isort .
	poetry run flake8 .
	poetry run mypy src tests

build: ## Build the CLI locally
	poetry run pyinstaller src/cli.py --clean --onefile --name nimbasms

clean: ## Clean build artifacts
	rm -rf dist/ build/ *.spec

release-patch: ## Create and push a patch release (0.0.X)
	@echo "Creating patch release..."
	poetry version patch
	git add pyproject.toml
	git commit -m "chore: bump patch version to $$(poetry version -s)"
	git tag v$$(poetry version -s)
	git push origin main
	git push origin v$$(poetry version -s)
	@echo "Release v$$(poetry version -s) created and pushed!"

release-minor: ## Create and push a minor release (0.X.0)
	@echo "Creating minor release..."
	poetry version minor
	git add pyproject.toml
	git commit -m "chore: bump minor version to $$(poetry version -s)"
	git tag v$$(poetry version -s)
	git push origin main
	git push origin v$$(poetry version -s)
	@echo "Release v$$(poetry version -s) created and pushed!"

release-major: ## Create and push a major release (X.0.0)
	@echo "Creating major release..."
	poetry version major
	git add pyproject.toml
	git commit -m "chore: bump major version to $$(poetry version -s)"
	git tag v$$(poetry version -s)
	git push origin main
	git push origin v$$(poetry version -s)
	@echo "Release v$$(poetry version -s) created and pushed!"

verify: ## Verify current environment and dependencies
	@echo "Python version:"
	python --version
	@echo "\nPip version:"
	pip --version
	@echo "\nPoetry version:"
	poetry --version
	@echo "\nInstalled dependencies:"
	poetry show