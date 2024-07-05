import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr


def _load_climate_data(input_file_path, bbox=None, filter_value=None):
    """
        Loads climate data from an input file
        and returns it on a xarray format.
        For the moment only grib files are accepted,
        but this function can be adapted to cover other file formats.

    Parameters
    ----------
        input_file_path: str, Path to the climate data to be loaded
        bbox: float list,
        Coordinates of the bounding box containing the zone of interest
        filter_value: int, When loading ECMWF data,
        value used to filter ensemble model number

        Returns
    -------
        DataFrame, A xarray with the data contained  in the input file

    """

    # Load climate data (grib or netcdf) into pandas dataframe.
    # Change this function if another data format is used
    if input_file_path.endswith(".grib"):
        input_xr = xr.open_dataset(input_file_path, engine="cfgrib")
    elif input_file_path.endswith(".nc"):
        input_xr = xr.open_dataset(input_file_path)

    # Filter only one ensemble model number when loading ECMWF
    if filter_value is not None:
        input_xr = input_xr.sel(number=filter_value)

    # Filter grid points within the zone of interest bounding box
    # Adding a buffer of 1deg to include nearby grid points
    if bbox is not None:
        lon_min, lat_min, lon_max, lat_max = bbox
        input_xr = input_xr.where(
            input_xr["longitude"] > lon_min - 1, drop=True
        )
        input_xr = input_xr.where(
            input_xr["longitude"] < lon_max + 1, drop=True
        )
        input_xr = input_xr.where(
            input_xr["latitude"] > lat_min - 1, drop=True
        )
        input_xr = input_xr.where(
            input_xr["latitude"] < lat_max + 1, drop=True
        )

    return input_xr


def _create_reference_grid(input_df, admin_df, admin_code_label):
    """
        Create a reference lat/lon grid based on the ECMWF grid.
        Also performs a geospatial join between the grid points
        and the admin boundaries.

    Parameters
    ----------
        input_df: DataFrame, Reference grid with lat/lon coordinates
        admin_df: GeoDataFrame, Admin boundaries used for aggregation analysis
        admin_code_label: str, Column name to be used as an unique admin code

        Returns
    -------
        GeoDataFrame,
        Reference lat/lon grid together with the link with admin boundaries

    """

    grid_df = input_df.copy()

    # Create point geoDataFrame from lat/lon grid.
    # Supposes the projection EPSG:4326
    grid_df = gpd.GeoDataFrame(
        grid_df,
        geometry=gpd.points_from_xy(grid_df.longitude, grid_df.latitude),
        crs="EPSG:4326",
    )
    # Create a square buffer around the point following the grid.
    # This is useful when doing the spatial join
    # with admin boundaries to include pixels
    # there are just outside of the admin boundary.
    # Specially necessary for
    # small admin boundaries.

    grid_df["geometry"] = grid_df["geometry"].buffer(0.5, cap_style=3)

    # Rename the admin code column name
    admin_df.rename(
        columns={admin_code_label: "adm_pcode"}, errors="ignore", inplace=True
    )

    admin_df = admin_df[["adm_pcode", "geometry"]]
    # Finds all grid points that are close to the admin boundary
    # (intersection with the square buffer)
    grid_df = grid_df.sjoin(admin_df, how="inner", predicate="intersects")

    # Returns the geometry to the lat/lon point grid
    grid_df = gpd.GeoDataFrame(
        grid_df,
        geometry=gpd.points_from_xy(grid_df.longitude, grid_df.latitude),
        crs="EPSG:4326",
    )
    grid_df = grid_df[
        ["pixel_geom_id", "adm_pcode", "geometry", "latitude", "longitude"]
    ]

    return grid_df


def _regrid_climate_data(input_df, ref_df, variable_name):
    """
    Re-gridding of a climate dataset
    following a reference dataset, both on a DataFrame format,
    The result is exported as a DataFrame file.
    It assumes that both grids are regular and that
    the reference grid is of lower resolution
    (the case for ERA5 and ECMWF as reference)


    Parameters
    ----------
    input_df: DataFrame, ERA5 Data Frame with originial grid
    ref_df: DataFrame, Reference grid with unique
    latitude/longitude values based on ECMWF
    variable_name: str, Variable name used in the aggregation.
    For ERA5 data this would be the
    Precipitation column name

    Returns
    -------
    DataFrame, Same as input_df but with
    latitude / longitude aligned with the reference grid.



    """
    df = input_df.copy()

    # create array with all unique lat/lon for both reference and era5 grids
    era5_lat = np.sort(np.unique(df["latitude"].values))
    era5_lon = np.sort(np.unique(df["longitude"].values))
    ref_lat = np.sort(np.unique(ref_df["latitude"].values))
    ref_lon = np.sort(np.unique(ref_df["longitude"].values))

    # compute the resolution of reference grid.
    # Assumes it is a regular grid (case for ECMWF data)
    ref_res_lat = ref_lat[1] - ref_lat[0]
    ref_res_lon = ref_lon[1] - ref_lon[0]

    #
    era5_new_lat = np.zeros(len(era5_lat))
    era5_new_lon = np.zeros(len(era5_lon))

    # loop through all latitude / longitude values and attribute a new value
    # based on the closest point of the reference grid.
    # If a grid point is too far
    # from the grid (based on the resolution)
    # do not attribute any value (np.nan)
    for i in range(0, len(era5_lat)):
        era5_new_lat[i] = ref_lat[(np.abs(ref_lat - era5_lat[i])).argmin()]
        if abs(era5_new_lat[i] - era5_lat[i]) > ref_res_lat / 2:
            era5_new_lat[i] = np.nan
        df.loc[df["latitude"] == era5_lat[i], "latitude"] = era5_new_lat[i]

    for i in range(0, len(era5_lon)):
        era5_new_lon[i] = ref_lon[(np.abs(ref_lon - era5_lon[i])).argmin()]
        if abs(era5_new_lon[i] - era5_lon[i]) > ref_res_lon / 2:
            era5_new_lon[i] = np.nan
        df.loc[df["longitude"] == era5_lon[i], "longitude"] = era5_new_lon[i]

    # Aggregates values (precipitation average) to the new low resolution grid
    df.dropna(inplace=True)
    col_list = list(df.columns.values)
    col_list.remove(variable_name)
    df.groupby(col_list)[variable_name].mean().reset_index()

    return df


def pre_process_ecmwf_data(
    input_file_path,
    admin_boundary_file_path,
    ref_grid_file_path,
    pixel_output_file_path,
    adm_output_file_path,
    admin_code_label,
):
    """
        Loads the ECMWF climate data grib file and converts it to a DataFrame.
        Also adapt columns names, precipitation units and link grid
        points to administrative boundaries.
        Finally, computes a reference grid
        by linking grid points to administrative boundaries.
        The process is executed ensemble model per ensemble model
        (out of 51 in total) to limit memory use.


    Parameters
    ----------
        input_file_path: str,
        Path to the ECMWF climate data grib file to be processed
        admin_boundary_file_path: str,
        Path to the admin boundary file to be used
        when aggregating grid points
        ref_grid_file_path: str, Path where the reference grid,
        combining both grid points and admin boundaries link,
        is to be exported
        pixel_output_file_path: str,
        Path where the processed file at the grid point
        level should be exported
        adm_output_file_path: str,
        Path where the processed file
        at the admin boundary level should be exported
        admin_code_label: str, Column name to be used as an unique admin code

        Returns
    -------

    """
    # Prints out progress
    print("pre-processing ECMWF data...")

    admin_df = gpd.read_file(admin_boundary_file_path)
    bbox = admin_df.geometry.unary_union.bounds

    # Load each ensemble model separately
    # for batch_number in range(0,51):
    for batch_number in range(0, 51):

        # Prints out progress
        if batch_number % 10 == 0:
            print(str(batch_number) + "/50")

        # Load ECMWF grib file (for one model at a time)
        input_xr = _load_climate_data(input_file_path, bbox, batch_number)
        # Converts ECMWF dataset into a dataframe
        df = input_xr.to_dataframe().dropna().reset_index()

        # Each data source uses a different unit
        # (meters/day for ERA5 and meters/second for ECMWF).
        # Converting both into mm/day here
        df["tp_mm_day"] = df["tprate"] * 1000 * 60 * 60 * 24

        # Compute lead time in months for ECMWF
        df["lead_time"] = 0
        for lead_days in df["step"].unique():
            lead_months = round(
                float(str(lead_days).split(" ")[0]) / 30
            )  # converting lead time in days into months
            df.loc[df["step"] == lead_days, "lead_time"] = lead_months

        # Correct valid time convention -
        # ECMWF prediction month ends on
        # the valid_time date so there is a 1-month shift
        df["valid_time_year"] = df["valid_time"].apply(lambda x: x.year)
        df["valid_time_month"] = df["valid_time"].apply(lambda x: x.month - 1)
        df.loc[df["valid_time_month"] == 0, "valid_time_year"] = (
            df.loc[df["valid_time_month"] == 0, "valid_time_year"] - 1
        )
        df.loc[df["valid_time_month"] == 0, "valid_time_month"] = 12

        # link to reference grid and retrieve pixel hash code and admin1 pcode
        df["pixel_geom_id"] = (
            df["latitude"].astype("str") + "-" + df["longitude"].astype("str")
        )
        df["pixel_geom_id"] = df["pixel_geom_id"].apply(lambda x: hash(x))
        lat_lon_df = df[["latitude", "longitude", "pixel_geom_id"]].copy()
        lat_lon_df = lat_lon_df.drop_duplicates()

        # Computes a reference grid by
        # linking grid points to administrative boundaries.
        # Only done once as all the ensemble models use the same spatial grid
        if batch_number == 0:
            grid_df = _create_reference_grid(
                lat_lon_df, admin_df, admin_code_label
            )

        # Link_df is a MxN link table between grid points
        # and administrative boundaries.
        # The groupby allows to drop grid points duplicate in the first case
        # or aggregate into admin boundaries in the second one

        link_df = pd.merge(
            df, grid_df, on="pixel_geom_id", suffixes=("", "_bis")
        )

        batch_data_grid_df = (
            link_df.groupby(
                [
                    "pixel_geom_id",
                    "latitude",
                    "longitude",
                    "number",
                    "valid_time_year",
                    "valid_time_month",
                    "lead_time",
                ]
            )["tp_mm_day"]
            .mean()
            .reset_index()
        )

        batch_data_adm_df = (
            link_df.groupby(
                [
                    "adm_pcode",
                    "number",
                    "valid_time_year",
                    "valid_time_month",
                    "lead_time",
                ]
            )["tp_mm_day"]
            .mean()
            .reset_index()
        )

        # Concatenate all ensemble model into a single DataFrame
        if batch_number == 0:
            data_grid_df = batch_data_grid_df
            data_adm_df = batch_data_adm_df
        else:
            data_grid_df = pd.concat([data_grid_df, batch_data_grid_df])
            data_adm_df = pd.concat([data_adm_df, batch_data_adm_df])

    data_grid_df.reset_index(inplace=True, drop=True)
    data_adm_df.reset_index(inplace=True, drop=True)

    # Export data to parquet file
    grid_df.to_parquet(ref_grid_file_path, compression="gzip")
    data_grid_df.to_parquet(pixel_output_file_path, compression="gzip")
    data_adm_df.to_parquet(adm_output_file_path, compression="gzip")

    # Prints out progress
    print("pre-processing ECMWF data - done")

    return


def pre_process_era5_data(
    era5_file_path,
    admin_boundary_file_path,
    ref_grid_file_path,
    pixel_output_file_path,
    adm_output_file_path,
):
    """
        Loads the ERA5 climate data grib file and converts it to a DataFrame.
        Also adapt columns names, precipitation units and link grid
        points to administrative boundaries.
        Exports the resulting DataFrame to a parquet file.


    Parameters
    ----------
        era5_file_path: str,
        Path to the ERA5 climate data grib file to be processed
        admin_boundary_file_path: str,
        Path to the admin boundary file
        to be used when aggregating grid points
        ref_grid_file_path: str, Path where the reference grid,
        combining both grid points
        and admin boundaries link, is to be exported
        pixel_output_file_path: str,
        Path where the processed file
        at the grid point level should be exported
        adm_output_file_path: str,
        Path where the processed file
        at the admin boundary level should be exported

        Returns
    -------

    """

    admin_df = gpd.read_file(admin_boundary_file_path)
    bbox = admin_df.geometry.unary_union.bounds

    # Load both ERA5 data (after regridding)
    input_xr = _load_climate_data(era5_file_path, bbox)
    era5_df = input_xr.to_dataframe().dropna().reset_index()
    grid_df = gpd.read_parquet(ref_grid_file_path)

    # Extract month and year information.
    if "valid_time" not in era5_df.columns:
        era5_df["valid_time"] = era5_df["time"]
    era5_df["valid_time_year"] = era5_df["valid_time"].apply(lambda x: x.year)
    era5_df["valid_time_month"] = era5_df["valid_time"].apply(
        lambda x: x.month
    )
    # Add column lead time (always 0 for ERA5)
    era5_df["lead_time"] = 0
    # Each source uses a different unit
    # (meters/day for ERA5 and meters/second for ECMWF).
    # Converting both into mm/day here
    era5_df["tp_mm_day"] = era5_df["tp"] * 1000

    # Regried ERA5 data to lower resolution.Link it to reference grid
    # and retrieve pixel hash code and admin1 pcode
    era5_regrided_df = _regrid_climate_data(era5_df, grid_df, "tp_mm_day")
    era5_regrided_df = pd.merge(
        era5_regrided_df, grid_df, on=["latitude", "longitude"]
    )
    data_grid_df = (
        era5_regrided_df.groupby(
            [
                "pixel_geom_id",
                "latitude",
                "longitude",
                "valid_time_year",
                "valid_time_month",
                "lead_time",
            ]
        )["tp_mm_day"]
        .mean()
        .reset_index()
    )
    data_adm_df = (
        era5_regrided_df.groupby(
            ["adm_pcode", "valid_time_year", "valid_time_month", "lead_time"]
        )["tp_mm_day"]
        .mean()
        .reset_index()
    )

    # Export data to parquet file
    data_grid_df.to_parquet(pixel_output_file_path, compression="gzip")
    data_adm_df.to_parquet(adm_output_file_path, compression="gzip")

    return


def ecmwf_bias_correction(ecmwf_file_path, era5_file_path):
    """
        Compute both the ECMWF lead-time bias and the bias (calibration)
        between ECMWF and ERA5. Add two columns with both bias corrections.
        Update the input ECMWF file with the new columns

    Parameters
    ----------
        ecmwf_file_path: str, Path to the processed ECMWF climate data
        era5_file_path: str, Path to the processed ERA5 climate data

        Returns
    -------

    """

    # Load ECMWF and ERA5 processed dataFrames from parquet files.
    ecmwf_df = pd.read_parquet(ecmwf_file_path)
    era5_df = pd.read_parquet(era5_file_path)

    # Detects which location is being used
    # (pixel or adminstrative boundary level)
    if "adm_pcode" in ecmwf_df.columns.values:
        geom_id = "adm_pcode"
    else:
        geom_id = "pixel_geom_id"

    ecmwf_corr_df = ecmwf_df.copy()

    # Computes average precipitation for a given location and month
    # (also model number and lead time in the case of ECMWF)
    ecmwf_corr_df["tp_mm_day_mean_raw"] = ecmwf_corr_df.groupby(
        ["number", geom_id, "valid_time_month", "lead_time"]
    )[["tp_mm_day"]].transform("mean")

    ecmwf_corr_df["tp_mm_day_mean_ref"] = ecmwf_corr_df.groupby(
        [geom_id, "valid_time_month"]
    )[["tp_mm_day"]].transform("mean")

    era5_avg_df = (
        era5_df.groupby([geom_id, "valid_time_month"])["tp_mm_day"]
        .mean()
        .reset_index()
    )

    ecmwf_corr_df = pd.merge(
        ecmwf_corr_df,
        era5_avg_df,
        on=["valid_time_month", geom_id],
        suffixes=("", "_mean_era5"),
    )

    # Correct bias by adding (or subtracting)
    # the average bias to every single prediction.
    # Limits the result to only positive values
    # (negative values are possible
    # when subtracting bias for small predictions)

    # Lead-time bias correction
    ecmwf_corr_df["tp_mm_day_bias_corrected"] = (
        ecmwf_corr_df["tp_mm_day"]
        - ecmwf_corr_df["tp_mm_day_mean_raw"]
        + ecmwf_corr_df["tp_mm_day_mean_ref"]
    )
    ecmwf_corr_df.loc[
        ecmwf_corr_df["tp_mm_day_bias_corrected"] < 0,
        "tp_mm_day_bias_corrected",
    ] = 0

    # ECMWF - ERA5 bias correction (calibration)
    ecmwf_corr_df["tp_mm_day_era5_calibrated"] = (
        ecmwf_corr_df["tp_mm_day"]
        - ecmwf_corr_df["tp_mm_day_mean_raw"]
        + ecmwf_corr_df["tp_mm_day_mean_era5"]
    )
    ecmwf_corr_df.loc[
        ecmwf_corr_df["tp_mm_day_era5_calibrated"] < 0,
        "tp_mm_day_era5_calibrated",
    ] = 0

    ecmwf_corr_df.drop(
        ["tp_mm_day_mean_raw", "tp_mm_day_mean_ref", "tp_mm_day_mean_era5"],
        inplace=True,
        axis=1,
    )

    ecmwf_corr_df.rename(columns={"tp_mm_day": "tp_mm_day_raw"}, inplace=True)

    # Export resulting ECMWF bias-corrected dataFrame to a parquet file
    ecmwf_corr_df.to_parquet(ecmwf_file_path, compression="gzip")

    return
