import os
from io import BytesIO, StringIO

import geopandas as gpd
import pandas as pd
from azure.storage.blob import BlobClient


def load_env_vars():
    """
    Loads required environment variables and checks their presence.
    Raises an error if any are missing.
    """
    sas_token = os.getenv("STORAGE_SAS_TOKEN_CHD")
    container_name = os.getenv("CONTAINER_NAME_CHD")
    storage_account = os.getenv("STORAGE_ACCOUNT_CHD")
    if not all([sas_token, container_name, storage_account]):
        raise EnvironmentError(
            "One or more required environment variables are missing."
        )
    return sas_token, container_name, storage_account


def upload_file(
    sas_token, container_name, storage_account, local_file_path, blob_path
):
    """
    Uploads a single file from 'local_file_path'
    to 'blob_path' in Azure Blob Storage.
    """
    base_url = f"https://{storage_account}.blob.core.windows.net"
    sas_url = f"{base_url}/{container_name}/{blob_path}" f"?{sas_token}"

    blob_client = BlobClient.from_blob_url(blob_url=sas_url)
    with open(local_file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
        print(f"Upload completed successfully for {blob_path}!")


def upload_stream(
    sas_token, container_name, storage_account, data_stream, blob_path
):
    """
    Uploads data from a BytesIO stream directly to Azure Blob Storage.
    """
    base_url = f"https://{storage_account}.blob.core.windows.net"
    sas_url = f"{base_url}/{container_name}/{blob_path}" f"?{sas_token}"

    blob_client = BlobClient.from_blob_url(blob_url=sas_url)
    blob_client.upload_blob(data_stream, overwrite=True)
    print(f"Stream upload completed successfully for {blob_path}!")


def download_file(
    sas_token, container_name, storage_account, blob_path, local_file_path
):
    """
    Downloads a blob from Azure Blob Storage to a local file path.
    """
    base_url = f"https://{storage_account}.blob.core.windows.net"
    sas_url = f"{base_url}/{container_name}/{blob_path}" f"?{sas_token}"

    blob_client = BlobClient.from_blob_url(blob_url=sas_url)
    download_stream = blob_client.download_blob()
    content = download_stream.readall()
    with open(local_file_path, "wb") as data:
        data.write(content)
        print(f"Download completed successfully for {blob_path}!")


def read_blob_to_dataframe(
    sas_token, container_name, storage_account, blob_path
):
    """
    Reads data from a blob at a specified path in
    Azure Blob Storage and returns it as a DataFrame.
    This function supports reading CSV and geospatial
    data formats such as SHP and GeoJSON.
    """
    base_url = f"https://{storage_account}.blob.core.windows.net"
    sas_url = f"{base_url}/{container_name}/{blob_path}" f"?{sas_token}"

    blob_client = BlobClient.from_blob_url(blob_url=sas_url)
    download_stream = blob_client.download_blob()
    content = download_stream.readall()
    if not content:
        print(f"The blob at {blob_path} is empty or could not be read.")
        return
    file_format = blob_path.split(".")[-1].lower()
    if file_format in ["csv"]:
        data_str = StringIO(content.decode("utf-8"))
        df = pd.read_csv(data_str)
    elif file_format in ["shp", "geojson"]:
        # Use GeoDataFrame for geospatial data
        data_bytes = BytesIO(content)
        df = gpd.read_file(
            data_bytes,
            driver="GeoJSON" if file_format == "geojson" else "ESRI Shapefile",
        )
    else:
        print(f"Unsupported file format: {file_format}")
        return None
    return df
