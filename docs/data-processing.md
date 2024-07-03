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

Inside the notebooks/ directory, create a new directory called data/:

```bash
mkdir -p notebooks/data
```

Copy the input_data/ directory from Google Drive into the newly created data/ directory.

### Start Jupyter Lab

run `jupyterlab`

```bash
poetry run jupyter lab
```

### Run Notebooks

* In your browser, navigate to the Jupyter Lab interface.
* First, open and run every cell in the ecmwf_pipeline.ipynb.
* After the pipeline notebook has completed, open and run ecmwf_analysis.ipynb to obtain the results.
