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

data-ecmwf:
	@echo "Automatically retrieving ECMWF data..."
	@poetry run python src/data_retrieval cds ecmwf --upload

data-era5:
	@echo "Automatically retrieving ERA5 data..."
	@poetry run python src/data_retrieval cds era5 --upload

data-pipeline: data-ecmwf data-era5
	@echo "Data extraction and upload pipeline completed."

help:
	@echo "Available make targets:"
	@echo " make help           - Print help"
	@echo " make .venv          - Install project dependencies"
	@echo " make hooks          - Add pre-commit hooks"
	@echo " make test           - Run unit tests"
	@echo " make lint           - Run lint tests"
	@echo " make clean          - Remove .venv"
	@echo ""