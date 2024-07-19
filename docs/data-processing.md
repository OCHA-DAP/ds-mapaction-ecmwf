# Data Processing

* [Setup](#setup)

![data processing architecture](./images/data-flow-diagram.svg)

### Setup

> **NOTE:** If you want to start fresh or remove an existing virtual environment, run:

```bash
make clean
```

> **NOTE:** Run the following command to create a virtual environment and install the necessary libraries using poetry through the Makefile

```bash
make .venv hooks
```

### Prepare Data Directory

Set up the data environment variables and paths in your Python script to manage data files and directories. Below is the example configuration:

```bash
mkdir -p ~/ma-chd-data/data/input_data
```

Copy the input_data/ directory from Google Drive into the newly created data/ directory.

### Data Directory Structure

> **NOTE:** Ensure that your directory structure under ~/ma-chd-data/data/ includes input_data/

### Start Jupyter Lab

run `jupyterlab`

```bash
poetry run jupyter lab
```

### Run Notebooks

* In your browser, navigate to the Jupyter Lab interface.
* First, open and run every cell in the ecmwf_pipeline.ipynb.
* After the pipeline notebook has completed, open and run ecmwf_analysis.ipynb to obtain the results.
