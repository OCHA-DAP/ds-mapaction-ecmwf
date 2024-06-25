from typing import List, Optional

import geopandas as gpd
import pandas as pd
import xarray as xr


def _load_climate_data(
    input_file_path: str,
    bbox: Optional[List[float]] = None,
    filter_value: Optional[int] = None,
) -> xr.Dataset:
    """
    Loads climate data from and input file and returns it on a xarray format.
    For the moment only grib files are accepted but this function can be
    adapted to cover other file formats.

    Parameters
    ----------
    input_file_path: str, Path to the climate data to be loaded
    bbox: float list, Coordinates of the bounding box containing the zone
                                        of interest
    filter_value: int, value used to filter ensemble model number when
                                        loading ECMWF data

    Returns
    -------
    xr.Dataset, Xarray Dataset with the data contained in the input file

    """
    # Load climate data (grib or netcdf) into pandas dataframe.
    # Change this function if another data format is used
    if input_file_path.endswith(".grib"):
        input_ds: xr.Dataset = xr.open_dataset(
            input_file_path, engine="cfgrib"
        )
    elif input_file_path.endswith(".nc"):
        input_ds: xr.Dataset = xr.open_dataset(input_file_path)

    # Filter only one ensemble model number when loading ECMWF
    if filter_value:
        input_ds = input_ds.sel(number=filter_value)

    # Filter grid points within the zone of interest bounding box
    # Adding a buffer of 1deg to include nearby grid points
    if bbox:
        lon_min, lat_min, lon_max, lat_max = bbox
        input_ds = input_ds.where(
            input_ds["longitude"] > lon_min - 1, drop=True
        )
        input_ds = input_ds.where(
            input_ds["longitude"] < lon_max + 1, drop=True
        )
        input_ds = input_ds.where(
            input_ds["latitude"] > lat_min - 1, drop=True
        )
        input_ds = input_ds.where(
            input_ds["latitude"] < lat_max + 1, drop=True
        )

    return input_ds


def _create_reference_grid(
    input_df: pd.DataFrame, admin_gdf: gpd.GeoDataFrame, admin_code_label: str
) -> gpd.GeoDataFrame:
    """
    Create a reference lat/lon grid based on the ECMWF grid.
    Also performs a geospatial join between the grid points
    and the admin boundaries.

    Parameters
    ----------
    input_df: DataFrame, Reference grid with lat/lon coordinates
    admin_gdf: GeoDataFrame, Admin boundaries used for aggregation analysis
    admin_code_label: str, Column name to be used as an unique admin code

    Returns
    -------
    GeoDataFrame, Reference lat/lon grid together with the link
                                with admin boundaries

    """
    grid_gdf = input_df.copy()

    # Create point geoDataFrame from lat/lon grid.
    # Supposes the projection EPSG:4326
    grid_gdf = gpd.GeoDataFrame(
        grid_gdf,
        geometry=gpd.points_from_xy(grid_gdf.longitude, grid_gdf.latitude),
        crs="EPSG:4326",
    )
    # Create a square buffer around the point following the grid.
    # This is useful when doing the spatial join with admin boundaries
    # to include pixels there are just outside of the admin boundary.
    # Specially necessary for small admin boundaries.
    grid_gdf["geometry"] = grid_gdf["geometry"].buffer(0.5, cap_style=3)

    # Rename the admin code column name
    admin_gdf.rename(
        columns={admin_code_label: "adm_pcode"}, errors="ignore", inplace=True
    )

    admin_gdf = admin_gdf[["adm_pcode", "geometry"]]
    # Finds all grid points that are close to the admin boundary
    # (intersection with the square buffer)
    grid_gdf = grid_gdf.sjoin(admin_gdf, how="inner", predicate="intersects")
    # Returns the geometry to the lat/lon point grid
    grid_gdf = gpd.GeoDataFrame(
        grid_gdf,
        geometry=gpd.points_from_xy(grid_gdf.longitude, grid_gdf.latitude),
        crs="EPSG:4326",
    )
    grid_gdf = grid_gdf[["pixel_geom_id", "adm_pcode", "geometry"]]

    return grid_gdf


def _compute_era5_climatology(input_df: pd.DataFrame, geom_id_label: str):
    """
    Compute the climatology per location (pixel or admin boundary)
    based one ERA5. The climatology includes the average precipitation
    per month but also different quantiles (50%, 33%, 25% and 20%)

    Parameters
    ----------
    input_df: DataFrame, DataFrame containing ERA5 climate data
    geom_id_label: str, Name of the column containing the unique geometry id.
                            It can be either pixel_geom_id or adm_pcode

    Returns
    -------
    DataFrame, Adds two set of columns (climatology_q and prob_q) to the input
                DataFrame. climatology_qX is the X% precipitation quantile for
                a given location and month. prob_qX has a value
                of 1 (0 otherwise) if, for a given location, month and year,
                the precipitation level is below the climatology
                X% precipitation quantile. The name "prob" is used to keep
                the same nomenclature of the ECMWF dataset where an ensemble
                model is used

    """
    df: pd.DataFrame = input_df.copy()

    # Compute climatology average and quantiles (50%, 33%, 25% and 20%)
    # for any given location and month
    climatology_era5_df: pd.DataFrame = (
        df.groupby([geom_id_label, "valid_time_month"])
        .agg(
            climatology_avg=("tp_mm_day", lambda x: x.mean()),
            climatology_q50=("tp_mm_day", lambda x: x.quantile(1 / 2)),
            climatology_q33=("tp_mm_day", lambda x: x.quantile(1 / 3)),
            climatology_q25=("tp_mm_day", lambda x: x.quantile(1 / 4)),
            climatology_q20=("tp_mm_day", lambda x: x.quantile(1 / 5)),
        )
        .reset_index()
    )

    df: pd.DataFrame = pd.merge(
        df, climatology_era5_df, on=[geom_id_label, "valid_time_month"]
    )

    # Computes, for a given location, month and year,
    # if the precipiation level is below the corresponding climatology quantile
    for q in ["50", "33", "25", "20"]:
        df["prob_q" + q] = (df["tp_mm_day"] <= df["climatology_q" + q]) * 1

    return df


def regrid_climate_data(
    era5_file_path: str, ecmwf_file_path: str, era5_regrid_file_path: str
):
    """
    Re-gridding of a climate dataset following a reference dataset. The result
    is exported as a NetCDF file. The current version uses the xesmf package


    Parameters
    ----------
    era5_file_path: str, Path to the ERA5 climate data to be processed
    ecmwf_file_path: str, Path to the climate data file used as a reference
                            grid (ECMWF)
    era5_regrid_file_path: str, Path to the ERA5 climate data after regridding

    Returns
    -------

    """
    from xesmf import Regridder

    # Re-grid of ERA5 data following the ECMWF grid (1deg)
    era_ds: xr.Dataset = _load_climate_data(era5_file_path)
    ecmwf_ds: xr.Dataset = _load_climate_data(ecmwf_file_path, None, 0)

    regridder = Regridder(era_ds, ecmwf_ds, "conservative")

    era1deg_ds: xr.Dataset = regridder(era_ds, keep_attrs=True)
    era1deg_ds.to_netcdf(era5_regrid_file_path)


def pre_process_ecmwf_data(
    input_file_path: str,
    admin_boundary_file_path: str,
    ref_grid_file_path: str,
    pixel_output_file_path: str,
    adm_output_file_path: str,
    admin_code_label: str,
):
    """
    Loads the ECMWF climate data grib file and converts it to a DataFrame.
    Also adapt columns names, precipitation units and link grid points to
    administrative boundaries. Finally, computes a reference grid by linking
    grid points to administrative boundaries. The process is executed ensemble
    model per ensemble model (out of 51 in total) to limit memory use.

    Parameters
    ----------
    input_file_path: str, Path to the ECMWF climate data grib file
                            to be processed
    admin_boundary_file_path: str, Path to the admin boundary file
                            to be used when aggregating grid points
    ref_grid_file_path: str, Path where the reference grid, combining both
                            grid points and admin boundaries link, is
                            to be exported
    pixel_output_file_path: str, Path where the processed file at the grid
                            point level should be exported
    adm_output_file_path: str, Path where the processed file at the admin
                            boundary level should be exported
    admin_code_label: str, Column name to be used as an unique admin code

    Returns
    -------

    """
    # Prints out progress
    print("pre-processing ECMWF data...")

    admin_df = gpd.read_file(admin_boundary_file_path)
    bbox = admin_df.geometry.unary_union.bounds

    # Executes each ensemble model separately
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

        # Correct valid time convention - ECMWF prediction month ends
        # on the valid_time date so there is a 1-month shift
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

        # Computes a reference grid by linking grid points to administrative
        # boundaries. Only done once as all the ensemble models use the same
        # spatial grid
        if batch_number == 0:
            grid_df = _create_reference_grid(
                lat_lon_df, admin_df, admin_code_label
            )

        # Link_df is a MxN link table between grid points and administrative
        # boundaries. The groupby allows to drop grid points duplicate in the
        # first case or aggregate into admin boundaries in the second one
        link_df = pd.merge(df, grid_df, on="pixel_geom_id")
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


def pre_process_era5_data(
    era5_file_path,
    admin_boundary_file_path,
    ref_grid_file_path,
    pixel_output_file_path,
    adm_output_file_path,
):
    """
    Loads the ERA5 climate data grib file and converts it to a DataFrame.
    Also adapt columns names, precipitation units and link grid points to
    administrative boundaries. Finally, computes the average climatology
    (per location and month) and export the resulting DataFrame to a
    parquet file.

    Parameters
    ----------
    era5_file_path: str, Path to the ERA5 climate data grib file
                            to be processed
    admin_boundary_file_path: str, Path to the admin boundary file
                            to be used when aggregating grid points
    ref_grid_file_path: str, Path where the reference grid, combining both
                            grid points and admin boundaries link,
                            is to be exported
    pixel_output_file_path: str, Path where the processed file at the
                            grid point level should be exported
    adm_output_file_path: str, Path where the processed file at the admin
                            boundary level should be exported

    Returns
    -------

    """
    admin_gdf = gpd.read_file(admin_boundary_file_path)
    bbox = admin_gdf.geometry.unary_union.bounds

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

    ##########################
    # ERA5 valid time is changed after the CDO grid matching, not sure why.
    # Using time here instead and adding a shift to correct it

    # TODO: check if the error persists with the new method used by Sarah
    # and drop these lines
    cdo_error = False
    if cdo_error:
        era5_df["valid_time_year"] = era5_df["time"].apply(lambda x: x.year)
        era5_df["valid_time_month"] = era5_df["time"].apply(
            lambda x: x.month + 1
        )
        era5_df.loc[era5_df["valid_time_month"] == 13, "valid_time_year"] = (
            era5_df.loc[era5_df["valid_time_month"] == 13, "valid_time_year"]
            + 1
        )
        era5_df.loc[era5_df["valid_time_month"] == 13, "valid_time_month"] = 1
    ##########################

    # Link to reference grid and retrieve pixel hash code and admin1 pcode
    geo_df = gpd.GeoDataFrame(
        era5_df,
        geometry=gpd.points_from_xy(era5_df.longitude, era5_df.latitude),
        crs="EPSG:4326",
    )
    geo_df = geo_df.sjoin_nearest(grid_df, max_distance=0.1)
    data_grid_df = (
        geo_df.groupby(
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
        geo_df.groupby(
            ["adm_pcode", "valid_time_year", "valid_time_month", "lead_time"]
        )["tp_mm_day"]
        .mean()
        .reset_index()
    )

    # Compute ERA5 climatology
    data_grid_df = _compute_era5_climatology(data_grid_df, "pixel_geom_id")
    data_adm_df = _compute_era5_climatology(data_adm_df, "adm_pcode")

    # Export data to parquet file
    data_grid_df.to_parquet(pixel_output_file_path, compression="gzip")
    data_adm_df.to_parquet(adm_output_file_path, compression="gzip")


def ecmwf_bias_correction(
    ecmwf_file_path: str, era5_file_path: str, output_file_path: str
):
    """
    Compute the bias between the average precipitation prediction
    (ECMWF) and ground truth (ERA5) per location, month, model and lead time.
    Correct the bias for every individual prediction.

    Parameters
    ----------
    ecmwf_file_path: str, Path to the processed ECMWF climate data
    era5_file_path: str, Path to the processed ERA5 climate data
    output_file_path: str, Path where the bias-corrected ECMWF file
                            should be exported

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
    era5_avg_df = (
        era5_df.groupby([geom_id, "valid_time_month"])["tp_mm_day"]
        .mean()
        .reset_index()
    )
    ecmwf_avg_df = (
        ecmwf_df.groupby(["number", geom_id, "valid_time_month", "lead_time"])[
            ["tp_mm_day"]
        ]
        .mean()
        .reset_index()
    )

    # Compute bias between the average precipitation
    # per location, month, model and lead time
    avg_df = pd.merge(
        ecmwf_avg_df,
        era5_avg_df,
        on=["valid_time_month", geom_id],
        suffixes=("_ecmwf", "_era5"),
    )
    avg_df["bias"] = avg_df["tp_mm_day_ecmwf"] - avg_df["tp_mm_day_era5"]
    avg_df.drop(["tp_mm_day_ecmwf", "tp_mm_day_era5"], inplace=True, axis=1)

    # Correct the bias by adding (or subtracting) the average bias to every
    # single prediction. Limits the result to only positive values
    # negative values are possible when subtracting bias for small predictions
    ecmwf_corr_df = pd.merge(
        ecmwf_corr_df,
        avg_df,
        on=["number", "valid_time_month", geom_id, "lead_time"],
    )
    ecmwf_corr_df["tp_mm_day"] = (
        ecmwf_corr_df["tp_mm_day"] - ecmwf_corr_df["bias"]
    )
    ecmwf_corr_df.loc[ecmwf_corr_df["tp_mm_day"] < 0, "tp_mm_day"] = 0
    ecmwf_corr_df.drop(["bias"], inplace=True, axis=1)

    # Export resulting ECMWF bias-corrected dataFrame to a parquet file
    ecmwf_corr_df.to_parquet(output_file_path, compression="gzip")


def compute_quantile_probability(
    input_file_path: str, climatology_file_path: str, output_file_path: str
):
    """
    Computes the probability of the ECMWF predicted precipitation being under
    different quantile thresholds foe every location, month and year.
    Quantiles thresholds are computd from ERA5 climatology for a given location
    and month. Different thresholds are used following the quantiles values
    (quantiles 50%, 33%, 25% and 20%). Probability is based on the share of
    ECMWF model predicting a below quantile value. Individual predictions bias
    and mean absolute error are also computed.

    Parameters
    ----------
    input_file_path: str, Path to the processed ECMWF climate data
                            (before or after bias correction)
    climatology_file_path: str, Path to the processed ERA5 climate data
                            containing the climatology data
    output_file_path: str, Path where the computed quantiles probability and
                            bias / maae score ECMWF file should be exported

    Returns
    -------

    """
    # Load ECMWF and ERA5 processed dataFrames from parquet files.
    ecmwf_prob_df = pd.read_parquet(input_file_path)
    era5_df = pd.read_parquet(climatology_file_path)

    # Detects which location is being used
    # (pixel or adminstrative boundary level)
    if "adm_pcode" in ecmwf_prob_df.columns.values:
        geom_id = "adm_pcode"
    else:
        geom_id = "pixel_geom_id"

    # Extracts the climatology per location and month
    # (every year has the same value)
    climatology_era5_df = era5_df[
        [
            geom_id,
            "valid_time_month",
            "climatology_q50",
            "climatology_q33",
            "climatology_q25",
            "climatology_q20",
        ]
    ].drop_duplicates()
    # Merges ECMWF dataFrame with the corresponding ERA5 climatology
    ecmwf_prob_df = pd.merge(
        ecmwf_prob_df, climatology_era5_df, on=[geom_id, "valid_time_month"]
    )

    # Compute a flag (1 or 0) to indicates if a given prediction
    # (location, month, year and ensemble model number) is below the
    # ERA5 climatology for the same location and month. This is used
    # later to compute the probability based on all models
    for q in ["50", "33", "25", "20"]:
        ecmwf_prob_df["prob_q" + q] = (
            ecmwf_prob_df["tp_mm_day"] <= ecmwf_prob_df["climatology_q" + q]
        ) * 1

    # Combine all model predictions into a single average value plus the
    # probability of it being under each climatology quantile.
    ecmwf_prob_df = (
        ecmwf_prob_df.groupby(
            [geom_id, "valid_time_year", "valid_time_month", "lead_time"]
        )[["tp_mm_day", "prob_q50", "prob_q33", "prob_q25", "prob_q20"]]
        .mean()
        .reset_index()
    )

    # Compute bias and MAE (mean absolute error) for every single
    # ECMWF prediction compared to ERA5 values
    ecmwf_prob_df = pd.merge(
        ecmwf_prob_df,
        era5_df,
        on=[geom_id, "valid_time_year", "valid_time_month"],
        suffixes=("", "_era5"),
        how="left",
    )
    ecmwf_prob_df["bias"] = (
        ecmwf_prob_df["tp_mm_day"] - ecmwf_prob_df["tp_mm_day_era5"]
    )
    ecmwf_prob_df["mae"] = abs(ecmwf_prob_df["bias"])

    # Export resulting ECMWF dataFrame to a parquet file
    ecmwf_prob_df.to_parquet(output_file_path, compression="gzip")
