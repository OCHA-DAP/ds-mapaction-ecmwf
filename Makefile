.PHONY: all
all: help

IMAGE_NAME="mapaction-img"


.venv:
	@echo "Installing project dependencies.."
	@poetry install --no-root

hooks:
	@echo "Adding pre-commit hooks.."
	@poetry run pre-commit install

test:
	@echo "Running unit tests.."
	@poetry run python -m pytest

lint:
	@echo "Running lint tests.."
	@poetry run pre-commit run --all-files

clean:
	@echo "Removing .venv"
	@rm -rf .venv
	@poetry env remove --all

docker-build:
	@echo "Building Docker image.."
	@docker compose build --no-cache

docker-run:
	@echo "Starting container.."
	@docker compose run --rm mapaction

docker-clean:
	@echo "Deleting Docker image.."
	@docker image rm $(IMAGE_NAME)


help:
	@echo "Available make targets:"
	@echo " make help           - Print help"
	@echo " make .venv          - Install project dependencies"
	@echo " make hooks          - Add pre-commit hooks"
	@echo " make test           - Run unit tests"
	@echo " make lint           - Run lint tests"
	@echo " make clean          - Remove .venv"
	@echo " make docker-build   - Build Docker image"
	@echo " make docker-run     - Start container"
	@echo " make docker-clean   - Delete Docker image"
	@echo ""
