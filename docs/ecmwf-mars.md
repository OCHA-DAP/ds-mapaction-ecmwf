# ECMWF MARS

* [Configure MARS API](#configure-mars-api)
* [ECMWF MARS Chad](#ecmwf-mars-chad)
* [Reference material](#reference-material)
* [Troubleshooting](#troubleshooting)

### Configure MARS API

Get your user API key i.e. `123456789abcdefg123456789abcdefg`  
registered to your e-mail address i.e. `your.name@company.com`

and write it into the configuration file, so it looks like:

```bash
$ cat ~/.ecmwfapirc
{
    "url"   : "https://api.ecmwf.int/v1",
    "key"   : "123456789abcdefg123456789abcdefg",
    "email" : "your.name@company.com"
}
```

### ECMWF MARS Chad

To retrieve ECMWF MARS data set for Chad,  
navigate to the root directory

```bash
cd ds-mapaction-ecmwf/
```

and run

```bash
poetry run python src/download_mars_seas5_chad.py
```

### Reference material

:book: [MARS user documentation](https://confluence.ecmwf.int/display/UDOC/MARS+user+documentation)

:book: [MARS server activity](https://apps.ecmwf.int/mars-activity/)

:book: [ECMWF Service status](https://www.ecmwf.int/en/service-status)

### Troubleshooting
