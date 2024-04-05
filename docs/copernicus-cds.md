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

and run

```bash
poetry run python src/data_retrieval/ecmwf_forecast_global_cds.py
```

Your request will be placed in a queue, and the process will wait for your turn.  
You should see something like this:

```bash
$ poetry run python src/data_retrieval/ecmwf_forecast_global_cds.py
2024-04-04 20:42:00,523 INFO Welcome to the CDS
2024-04-04 20:42:00,523 INFO Sending request to https://cds.climate.copernicus.eu/api/v2/resources/seasonal-monthly-single-levels
2024-04-04 20:42:00,632 INFO Request is queued

```

This can take a few minutes. Eventually a progress bar will appear once the download starts. You should see something like this once the download is complete:

```bash
$ poetry run python src/data_retrieval/ecmwf_forecast_global_cds.py
2024-04-04 20:42:00,523 INFO Welcome to the CDS
2024-04-04 20:42:00,523 INFO Sending request to https://cds.climate.copernicus.eu/api/v2/resources/seasonal-monthly-single-levels
2024-04-04 20:42:00,632 INFO Request is queued
2024-04-04 20:56:20,893 INFO Request is completed
2024-04-04 20:56:20,894 INFO Downloading https://download-0012-clone.copernicus-climate.eu/cache-compute-0012/cache/data2/adaptor.mars.external-1712260115.8642066-16228-7-0f47878d-bd10-41c3-9471-9000c4a77b3a.grib to /home/<your-username>/Downloads/ECMWF_Global_Forecast/ecmwf_forecast_global_all_years.grib (10.9G)
2024-04-04 22:25:34,412 INFO Download rate 2.1M/s
Downloaded: /home/<your-username>/Downloads/ECMWF_Global_Forecast/ecmwf_forecast_global_all_years.grib
```

### ERA5 CDS

To retrieve `reanalysis-era5-single-levels-monthly-means` data set,  
navigate to the root directory

```bash
cd ds-mapaction-ecmwf/
```

and run

```bash
poetry run python src/data_retrieval/era5_forecast_global_cds.py
```

Your request will be placed in a queue, and the process will wait for your turn.  
You should see something like this:

```bash
$ poetry run python src/data_retrieval/era5_forecast_global_cds.py
2024-04-04 20:23:51,375 INFO Welcome to the CDS
2024-04-04 20:23:51,376 INFO Sending request to https://cds.climate.copernicus.eu/api/v2/resources/reanalysis-era5-single-levels-monthly-means
2024-04-04 20:23:51,479 INFO Request is queued

```

This can take a few minutes. Eventually a progress bar will appear once the download starts. You should see something like this once the download is complete:

```bash
$ poetry run python src/data_retrieval/era5_forecast_global_cds.py
2024-04-04 20:23:51,375 INFO Welcome to the CDS
2024-04-04 20:23:51,376 INFO Sending request to https://cds.climate.copernicus.eu/api/v2/resources/reanalysis-era5-single-levels-monthly-means
2024-04-04 20:23:51,479 INFO Request is queued
2024-04-04 20:30:10,427 INFO Request is completed
2024-04-04 20:30:10,428 INFO Downloading https://download-0018.copernicus-climate.eu/cache-compute-0018/cache/data9/adaptor.mars.internal-1712258651.2068512-13809-14-ab916075-1f16-46d2-9539-06fef81667a1.grib to /home/<your-username>/Downloads/ERA5_Global_Data/ERA5_total_precipitation_global_1981_2023_all_months.grib (1021.9M)
2024-04-04 20:37:16,196 INFO Download rate 2.4M/s
Downloaded: /home/<your-username>/Downloads/ERA5_Global_Data/ERA5_total_precipitation_global_1981_2023_all_months.grib
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
