# Copernicus Climate Data Store (CDS)

* [Configure CDS API](#configure-cds-api)
* [ECMWF CDS](#ecmwf-cds)
* [ERA5 CDS](#era5-cds)
* [Troubleshooting](#troubleshooting)

### Configure CDS API

Get your user ID (UID) and API key from the **[CDS portal](https://cds.climate.copernicus.eu/user)**

and write it into the configuration file, so it looks like:

```bash
$ cat ~/.cdsapirc
url: https://cds.climate.copernicus.eu/api/v2
key: <UID>:<API key>
verify: 1
```

### ECMWF CDS

To retrieve `seasonal-monthly-single-levels` data set,  
navigate to the root directory

```bash
cd ds-mapaction-ecmwf/
```

and run one of the following options:

Download Locally to the Default Directory:

```bash
poetry run python src/data_retrieval cds ecmwf
```

Specify a Custom Local Path:

```bash
poetry run python src/data_retrieval cds ecmwf --local /path/to/save
```

Upload to the Cloud:

```bash
poetry run python src/data_retrieval cds ecmwf --upload
```

Your request will be placed in a queue, and the process will wait for your turn.  
You should see something like this:

```bash
$ poetry run python src/data_retrieval cds ecmwf
INFO,__main__,2024-04-21 15:40:11,878,Downloading Copernicus CDS data of ECMWF global forecast..
2024-04-21 15:40:12,119 INFO Welcome to the CDS
2024-04-21 15:40:12,119 INFO Sending request to https://cds.climate.copernicus.eu/api/v2/resources/seasonal-monthly-single-levels
2024-04-21 15:40:12,229 INFO Request is queued

```

This can take a few minutes. Eventually a progress bar will appear once the download starts. You should see something like this once the download is complete:

```bash
$ poetry run python src/data_retrieval cds ecmwf
INFO,__main__,2024-04-21 15:40:11,878,Downloading Copernicus CDS data of ECMWF global forecast..
2024-04-21 15:40:12,119 INFO Welcome to the CDS
2024-04-21 15:40:12,119 INFO Sending request to https://cds.climate.copernicus.eu/api/v2/resources/seasonal-monthly-single-levels
2024-04-21 15:40:12,229 INFO Request is queued
2024-04-21 15:40:13,282 INFO Request is running
2024-04-21 15:48:31,476 INFO Request is completed
2024-04-21 15:48:31,476 INFO Downloading https://download-0004-clone.copernicus-climate.eu/cache-compute-0004/cache/data5/adaptor.mars.external-1713710412.4266803-14909-8-7ea73840-0e75-4abd-afd6-7923f56d40ee.grib to /home/<your-username>/Downloads/ecmwf_global_forecast/ecmwf_forecast_global_all_years.grib (10.9G)
2024-04-21 16:38:27,693 INFO Download rate 3.7M/s
Downloaded: /home/<your-username>/Downloads/ecmwf_global_forecast/ecmwf_forecast_global_all_years.grib
```

### ERA5 CDS

To retrieve `reanalysis-era5-single-levels-monthly-means` data set,  
navigate to the root directory

```bash
cd ds-mapaction-ecmwf/
```

And run one of the following options to download the data on the default .grib format:  

```bash
poetry run python src/data_retrieval cds era5
```

```bash
poetry run python src/data_retrieval cds era5 --local /path/to/save
```

```bash
poetry run python src/data_retrieval cds era5 --upload
```

Or you can specify which format to download [ grib or netcdf ] by running one of the following options:

```bash
poetry run python src/data_retrieval cds era5 --format netcdf
```

```bash
poetry run python src/data_retrieval cds era5 --format netcdf --local ~/Downloads/test2_era5
```

```bash
poetry run python src/data_retrieval cds era5 --format [grib or netcdf] --upload
```

Your request will be placed in a queue, and the process will wait for your turn.  
You should see something like this:

```bash
$ poetry run python src/data_retrieval cds era5
INFO,__main__,2024-04-21 15:32:30,623,Downloading Copernicus CDS data of ERA5 total precipitation..
2024-04-21 15:32:30,927 INFO Welcome to the CDS
2024-04-21 15:32:30,928 INFO Sending request to https://cds.climate.copernicus.eu/api/v2/resources/reanalysis-era5-single-levels-monthly-means
2024-04-21 15:32:31,479 INFO Request is queued

```

This can take a few minutes. Eventually a progress bar will appear once the download starts. You should see something like this once the download is complete:

```bash
$ poetry run python src/data_retrieval cds era5
INFO,__main__,2024-04-21 15:32:30,623,Downloading Copernicus CDS data of ERA5 total precipitation..
2024-04-21 15:32:30,927 INFO Welcome to the CDS
2024-04-21 15:32:30,928 INFO Sending request to https://cds.climate.copernicus.eu/api/v2/resources/reanalysis-era5-single-levels-monthly-means
2024-04-21 15:32:30,979 INFO Request is queued
2024-04-21 15:32:31,222 INFO Request is completed
2024-04-21 15:32:31,222 INFO Downloading https://download-0007-clone.copernicus-climate.eu/cache-compute-0007/cache/data9/adaptor.mars.internal-1713646916.8955271-14317-8-247ce0bd-b725-48bc-8d4a-0a301ee2e918.grib to /home/<your-username>/Downloads/era5_global_data/era5_total_precipitation_global_1981_2023_all_months.grib (1021.9M)
2024-04-21 15:37:47,581 INFO Download rate 3.2M/s
Downloaded: /home/<your-username>/Downloads/era5_global_data/era5_total_precipitation_global_1981_2023_all_months.grib
```

### Troubleshooting

Most common issues

#### Licence agreement error

If you are getting a following error:

```bash
Exception: Client has not agreed to the required terms and conditions..
To access this resource, you first need to accept the terms of
'Additional licence to use non European contributions'
at https://cds.climate.copernicus.eu/cdsapp/#!/terms/Additional-licence-to-use-non-European-contributions
To access this resource, you first need to accept the termsof 'Licence to use Copernicus Products'
at https://cds.climate.copernicus.eu/cdsapp/#!/terms/licence-to-use-copernicus-products
```

It means that you have created your CDS credentials but did not accept the licensing agreement. Navigate to the websites provided by the URL links in the error message, log in using your user credentials, and accept the terms and conditions. Then, try to run the script again.

#### Getting InsecureRequestWarning from urllib3

If you are getting a following warning:

```bash
.../ds-mapaction-ecmwf/.venv/lib/python3.10/site-packages/urllib3/connectionpool.py:1103:
InsecureRequestWarning: Unverified HTTPS request is being made to host 'cds.climate.copernicus.eu'.
Adding certificate verification is strongly advised.
See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#tls-warnings
```

you may have disabled the `HTTPS request verification` by setting  
the parameter in your `~/.cdsapirc` file to

```bash
verify: 0
```

open your `~/.cdsapirc` file again and set the value to

```bash
verify: 1
```

your `~/.cdsapirc` file should now look similar to the example in [Configure CDS API](#configure-cds-api),  
which should fix the warning.
