# ECMWF Seasonal Forecast Historical Analysis

|   |   |
|---|---|
|Project|[![Python Versions](https://img.shields.io/badge/Python-3.8%20%7C%203.9%20%7C%203.10-blue?logo=python&logoColor=white)](https://www.python.org/) [![License](https://img.shields.io/github/license/OCHA-DAP/ds-mapaction-ecmwf)](LICENSE) [![GitHub top language](https://img.shields.io/github/languages/top/OCHA-DAP/ds-mapaction-ecmwf)](https://github.com/OCHA-DAP/ds-mapaction-ecmwf)|
|Quality| [![Issues](https://img.shields.io/github/issues/OCHA-DAP/ds-mapaction-ecmwf)](https://github.com/OCHA-DAP/ds-mapaction-ecmwf/issues) |
| Tools | [![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/) [![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/) [![Jupyter](https://img.shields.io/badge/Jupyter-gray?logo=jupyter&labelColor=grey&color=orange&logoColor=orange)](https://jupyter.org/) |
|Community|[![Maintenance](https://img.shields.io/badge/Maintained-yes-green)](https://github.com/OCHA-DAP/ds-mapaction-ecmwf/graphs/commit-activity) [![Stars](https://img.shields.io/github/stars/OCHA-DAP/ds-mapaction-ecmwf)](https://github.com/OCHA-DAP/ds-mapaction-ecmwf)  [![Forks](https://img.shields.io/github/forks/OCHA-DAP/ds-mapaction-ecmwf)](https://github.com/OCHA-DAP/ds-mapaction-ecmwf/network/members)  [![Contributors](https://img.shields.io/github/contributors/OCHA-DAP/ds-mapaction-ecmwf)](https://github.com/OCHA-DAP/ds-mapaction-ecmwf/graphs/contributors)  [![Commit activity](https://img.shields.io/github/commit-activity/m/OCHA-DAP/ds-mapaction-ecmwf)](https://github.com/OCHA-DAP/ds-mapaction-ecmwf/commits/main)|
|Maintainers|[![UN-OCHA](https://img.shields.io/badge/-UN%20OCHA-black?logo=linkedin&colorB=gray)](https://www.linkedin.com/company/united-nations-ocha/) [![MapAction](https://img.shields.io/badge/-MapAction-black?logo=linkedin&colorB=gray)](https://www.linkedin.com/company/mapaction/)|

* [Overview](#overview)
* [Development](#development)
  * [Installing Poetry](#installing-poetry)
  * [Installing dependencies](#installing-dependencies)
  * [Lint and format](#lint-and-format)

## Overview

This repository contains the analysis of the ECMWF seasonal forecasts,
done in collaboration with MapAction.

## Development

We use **[Poetry](https://python-poetry.org/)** for package management. Poetry is production tested dependency management tool with exact version locking and support for packaging and virtual environments.

### Installing Poetry

:book: [Install Poetry on Linux, macOS, Windows (WSL)](https://python-poetry.org/docs/#installing-with-the-official-installer) using the official installer

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

if necessary, add poetry location to `PATH`

```bash
echo 'export POETRY_HOME="$HOME/.local/bin"' >> ~/.bashrc

echo 'export PATH="$POETRY_HOME:$PATH"' >> ~/.bashrc

. ~/.bashrc
```

test that installation was successful

```bash
poetry --version
```

### Installing dependencies

Before you start developing in this repository,  
you will need to install project dependencies and pre-commit Git hooks.

navigate to the project directory

```bash
cd ds-mapaction-ecmwf
```

and run

```bash
make .venv hooks
```

or if you do not have `make` on your OS (i.e. Windows), you can run

```bash
# first install all dependencies
poetry install --no-root

# then install Git hooks
poetry run pre-commit install
```

**NOTE:** any new package can be added to the project by running

```bash
poetry add [package-name]
```

### Lint and format

All code is formatted according to [black](https://black.readthedocs.io/en/stable/), [flake8](https://flake8.pycqa.org/en/latest/), and [PyMarkdown](https://github.com/jackdewinter/pymarkdown) guidelines.  
The repo is set-up to trigger lint tests automatically on each commit using [pre-commit](https://pre-commit.com/).

You can also run lint tests manually using

```bash
make lint
```

or if you do not have `make` on your OS (i.e. Windows), you can run

```bash
poetry run pre-commit run --all-files
```

This is especially useful if you try to resolve some failed test.  
Once you passed all tests, you should see something like this

```bash
$ make lint
Running lint tests..
black....................................................................Passed
isort....................................................................Passed
flake8...................................................................Passed
pymarkdown...............................................................Passed
```

## Project Structure

Below is the directory and file structure of the project, providing a quick overview of the key components:

### Directory Structure

* **`.github/`**: The directory is a special folder used by GitHub to store GitHub Actions workflows and other GitHub-specific configuration files.

* **`.flake8`**: The .flake8 file is a configuration file for the `flake8` tool, which is used to enforce coding style and standards in Python projects.

* **`.gitignore`**: This .gitignore file is comprehensive and covers a wide range of files that are typically not needed in version control for Python projects, ensuring that only relevant source code and resources are included in the repository.

* **`.pre-commit-config.yaml`**: The file .pre-commit-config.yaml configures pre-commit hooks for the project, specifying tools like `black`, `isort`, `flake8`, and `pymarkdown` for code formatting and linting, as well as `nbqa-black` for Jupyter Notebook formatting. It is set to fail fast, stopping at the first encountered error.

* **`docs/`**: Houses documentation for the project. This includes detailed information on various aspects of the project, including data storage, processing, and retrieval methods.

* **`notebooks/`**: Contains Jupyter notebooks such as `ecmwf_pipeline.ipynb`, `ecmwf_analysis.ipynb`, and others, which are used for interactive data analysis, visualisation, and demonstrating the project's results.

* **`src/`**: The source code directory where the project's main Python code resides. It is organised into subdirectories each focusing on different aspects of data handling and analysis. `data_retrieval/`: Features scripts like `azure_blob_utils.py` for interacting with Azure Blob Storage, a `cds/` subdirectory with modules (`common.py`, `ecmwf.py`, `era5.py`, `mars.py`) for retrieving climate data from different sources, and `util.py` for utility functions. The `main.py` serves as the entry point for data retrieval operations, and static_data/country_bbox.csv stores geographical bounding boxes for countries. `data_processing/`: Includes `custom_python_package.py` for custom data processing tasks and an `__init__.py` file indicating this directory is a Python package. `data_analysis`: Contains `ecmwf_data_analysis.py` for analysing data from the European Centre for Medium-Range Weather Forecasts (ECMWF).

* **`tests/`**: Contains test code for the project, ensuring that the software functions as expected.

* **`Makefile`**: This Makefile is designed to facilitate various operations such as dependency management, testing, linting, and data retrieval in a consistent and reproducible manner.

```text
.
├── .flake8
├── .github/
│ └── workflows/ci-test.yml
├── .gitignore
├── .pre-commit-config.yaml
├── docs/
│ ├── azure-blob-storage.md
│ ├── copernicus-cds.md
│ ├── data-processing.md
│ ├── ecmwf-mars.md
│ ├── images/
│ │ └── ...
│ └── README.md
├── LICENSE
├── Makefile
├── notebooks/
│ ├── .ipynb_checkpoints/
│ │ └── ...
│ ├── bounding-box-chad.ipynb
│ ├── bounding-box-tool.ipynb
│ ├── ecmwf_analysis.ipynb
│ ├── ecmwf_pipeline.ipynb
│ └── ecmwf_sandbox.ipynb
├── poetry.lock
├── pyproject.toml
├── README.md
├── src/
│ ├── data_analysis/
│ │ ├── ecmwf_data_analysis.py
│ │ └── pycache/
│ ├── data_processing/
│ │ ├── custom_python_package.py
│ │ ├── init.py
│ │ └── pycache/
│ └── data_retrieval/
│   ├── azure_blob_utils.py
│   ├── cds/
│   │ ├── common.py
│   │ ├── ecmwf.py
│   │ ├── era5.py
│   │ ├── init.py
│   │ └── mars.py
│   ├── init.py
│   ├── main.py
│   ├── pycache/
│   ├── static_data/country_bbox.csv
│   └── util.py
└── tests/
├── init.py
└── data_retrieval/
  ├── init.py
  └── cds/
    ├── init.py
    ├── test_common.py
    ├── test_ecmwf.py
    ├── test_era5.py
    └── test_mars.py
```
