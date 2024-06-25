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

We also use **[Docker](https://docs.docker.com/engine/install/ubuntu/)** development environement in cases where we need to work with libraries that depend on compiled binaries.

The minimum tested Docker version: `26.1.1`

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
