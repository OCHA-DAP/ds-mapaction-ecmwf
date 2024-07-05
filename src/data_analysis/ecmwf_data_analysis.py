import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import metrics


##################################################################
def compute_quantile_probability(input_df, quantile_value_list, tp_col_name):
    """
        Computes the probability of the ECMWF
        predicted precipitation being under different quantile thresholds
        for every location, month and year.
        Quantiles thresholds are computd from ERA5
        climatology for a given location and month.
        Different thresholds are used following the quantiles values
        (quantiles 50%, 33%, 25% and 20%).
        Probability is based on the share of ECMWF model predicting
        a below quantile value.
        Individual predictions bias and
        mean absolute error are also computed.



    Parameters
    ----------
        input_file_path: str,
        Path to the processed ECMWF climate data
        (before or after bias correction)
        climatology_file_path: str,
        Path to the processed ERA5 climate data
        containing the climatology data
        output_file_path: str,
        Path where the computed quantiles probability
        and bias / maae score ECMWF file should be exported

        Returns
    -------

    """

    df = input_df.copy()

    # Detects which location is being used
    # (pixel or adminstrative boundary level)
    if "adm_pcode" in df.columns.values:
        geom_id = "adm_pcode"
        column_list = [geom_id]
    else:
        geom_id = "pixel_geom_id"
        column_list = [geom_id, "latitude", "longitude"]

    column_list = column_list + [
        "valid_time_year",
        "valid_time_month",
        "lead_time",
        "tp_mm_day",
    ]

    if not isinstance(quantile_value_list, list):
        quantile_value_list = [quantile_value_list]

    # Computes climatology
    for quantile_value in quantile_value_list:
        # Compute climatology average and quantiles
        # for any given location and month
        quantile_label = ("climatology_q_" + "%.2f" % quantile_value).replace(
            ".", "_"
        )
        climatology_df = (
            df[
                (df["valid_time_year"] >= 1993)
                & (df["valid_time_year"] <= 2016)
            ]
            .groupby([geom_id, "valid_time_month"])[tp_col_name]
            .quantile(quantile_value)
            .reset_index()
        )
        climatology_df.rename(
            columns={tp_col_name: quantile_label}, inplace=True
        )
        df = pd.merge(df, climatology_df, on=[geom_id, "valid_time_month"])

        # Computes, for a given location, month and year, if the precipiation
        # level is below the corresponding climatology quantile
        below_precipitation_label = (
            "below_q_" + "%.2f" % quantile_value
        ).replace(".", "_")
        df[below_precipitation_label] = (
            df[tp_col_name] <= df[quantile_label]
        ) * 1

        # Combine the percentage (probability) of model with precipitation
        # level below the  corresponding climatology quantile
        prob_label = ("prob_q_" + "%.2f" % quantile_value).replace(".", "_")
        df[prob_label] = df.groupby(
            [geom_id, "valid_time_year", "valid_time_month", "lead_time"]
        )[below_precipitation_label].transform("mean")
        column_list.append(quantile_label)
        column_list.append(prob_label)

    # Computes model average and only keep the ensemble statistics
    df["tp_mm_day"] = df.groupby(
        [geom_id, "valid_time_year", "valid_time_month", "lead_time"]
    )[tp_col_name].transform("mean")
    df = df[column_list].drop_duplicates()

    return df


##################################################################
def prepare_climatology(ecmwf_df, era5_df):

    ecmwf_plot_df = (
        ecmwf_df.groupby(["valid_time_month", "lead_time"])[
            [
                "tp_mm_day_raw",
                "tp_mm_day_bias_corrected",
                "tp_mm_day_era5_calibrated",
            ]
        ]
        .mean()
        .reset_index()
    )
    era5_plot_df = (
        era5_df.groupby(["valid_time_month"])["tp_mm_day"].mean().reset_index()
    )

    return ecmwf_plot_df, era5_plot_df


##################################################################
def plot_climatology(ecmwf_plot_df, era5_plot_df, scope_text):

    fig, axs = plt.subplots(ncols=3, nrows=1, figsize=(15, 6))
    for col in range(3):

        ax = axs[col]

        if col == 0:
            bias_text = "ECMWF raw data"
            col_name = "tp_mm_day_raw"
        elif col == 1:
            bias_text = "ECMWF with leadtime bias correction"
            col_name = "tp_mm_day_bias_corrected"
        else:
            bias_text = "ECMWF with ERA5 calibration"
            col_name = "tp_mm_day_era5_calibrated"

        ax.plot(
            era5_plot_df["valid_time_month"],
            era5_plot_df["tp_mm_day"],
            label="era5",
        )
        for i in range(1, 7):
            ecmwf_leadtime_plot_df = ecmwf_plot_df[
                ecmwf_plot_df["lead_time"] == i
            ]
            ax.plot(
                ecmwf_leadtime_plot_df["valid_time_month"],
                ecmwf_leadtime_plot_df[col_name],
                label="lead_time: " + str(i),
            )

        ax.set_title(
            "Precipitation bias per month and lead time \n("
            + scope_text
            + ") \n "
            + bias_text
        )
        ax.set_xlabel("month")
        ax.set_ylabel("precipitation bias (mm / day)")

        ax.legend(loc="best")

    return


##################################################################
def prepare_leadtime_month_dependency(ecmwf_df, era5_df, month_range):

    if "adm_pcode" in ecmwf_df.columns.values:
        geom_id = "adm_pcode"
    else:
        geom_id = "pixel_geom_id"

    ecmwf_df = (
        ecmwf_df.groupby(
            [geom_id, "valid_time_year", "valid_time_month", "lead_time"]
        )[
            [
                "tp_mm_day_raw",
                "tp_mm_day_bias_corrected",
                "tp_mm_day_era5_calibrated",
            ]
        ]
        .mean()
        .reset_index()
    )

    plot_df = pd.merge(
        ecmwf_df,
        era5_df,
        on=[geom_id, "valid_time_year", "valid_time_month"],
        suffixes=["", "_era5"],
    )
    plot_df = plot_df[plot_df["valid_time_month"].isin(month_range)]

    bias_mae_col_list = []

    for tp_col_name in [
        "tp_mm_day_raw",
        "tp_mm_day_bias_corrected",
        "tp_mm_day_era5_calibrated",
    ]:
        bias_col_name = tp_col_name + "_bias"
        mae_col_name = tp_col_name + "_mae"
        plot_df[bias_col_name] = plot_df[tp_col_name] - plot_df["tp_mm_day"]
        plot_df[mae_col_name] = abs(plot_df[bias_col_name])
        bias_mae_col_list.append(bias_col_name)
        bias_mae_col_list.append(mae_col_name)

    plot_df = (
        plot_df.groupby("lead_time")[bias_mae_col_list].mean().reset_index()
    )

    return plot_df


##################################################################
def plot_leadtime_month_dependency(plot_df, scope_text):

    fig, axs = plt.subplots(ncols=2, nrows=1, figsize=(15, 6))

    for col in range(2):

        ax = axs[col]

        if col == 0:
            ax.plot(
                plot_df["lead_time"],
                plot_df["tp_mm_day_raw_bias"],
                label="ECMWF raw data",
            )
            ax.plot(
                plot_df["lead_time"],
                plot_df["tp_mm_day_bias_corrected_bias"],
                label="ECMWF with leadtime bias correction",
            )
            ax.plot(
                plot_df["lead_time"],
                plot_df["tp_mm_day_era5_calibrated_bias"],
                label="ECMWF with ERA5 calibration",
            )
            ax.set_title(
                "ECMWF - ERA5 Bias evolution with lead time ("
                + scope_text
                + ")"
            )
            ax.set_ylabel("Bias (mm/day)")
        else:
            ax.plot(
                plot_df["lead_time"],
                plot_df["tp_mm_day_raw_mae"],
                label="ECMWF raw data",
            )
            ax.plot(
                plot_df["lead_time"],
                plot_df["tp_mm_day_bias_corrected_mae"],
                label="ECMWF with leadtime bias correction",
            )
            ax.plot(
                plot_df["lead_time"],
                plot_df["tp_mm_day_era5_calibrated_mae"],
                label="ECMWF with ERA5 calibration",
            )
            ax.set_title(
                "ECMWF - ERA5 MAE evolution with lead time ("
                + scope_text
                + ")"
            )
            ax.set_ylabel("MAE (mm/day)")
            # ax.set_ylim([-0.1,max(1.1*plot_df.mae.max(),1.1*plot_corr_df.mae.max())])

        ax.set_xlabel("lead time")
        ax.legend(loc="best")

    return


##################################################################
def plot_performance_analysis(
    ecmwf_df, era5_df, quantile_value_list, month_range
):

    if "adm_pcode" in ecmwf_df.columns.values:
        geom_id = "adm_pcode"
    else:
        geom_id = "pixel_geom_id"

    df = pd.merge(
        ecmwf_df,
        era5_df,
        on=[geom_id, "valid_time_year", "valid_time_month"],
        suffixes=["_ecmwf", "_era5"],
    )
    df = df[df["valid_time_month"].isin(month_range)]

    if not isinstance(quantile_value_list, list):
        quantile_value_list = [quantile_value_list]

    n_rows = len(quantile_value_list)

    fig, axs = plt.subplots(ncols=3, nrows=n_rows, figsize=(15, 6 * n_rows))

    for row in range(n_rows):

        threshold_list = np.arange(0, 1.1, 0.1).tolist()
        leadtime_list = df["lead_time_ecmwf"].unique()
        mae_list = []
        accuracy_list = []
        f1_score_list = []
        quantile_value = quantile_value_list[row]
        quantile_label = "%.2f" % quantile_value
        ecmwf_prob_col_name = ("prob_q_" + quantile_label + "_ecmwf").replace(
            ".", "_"
        )
        era5_prob_col_name = ("prob_q_" + quantile_label + "_era5").replace(
            ".", "_"
        )

        for leadtime in leadtime_list:
            mae_list_per_threshold = []
            accuracy_list_per_threshold = []
            f1_score_list_per_threshold = []

            y_true = df.loc[
                df["lead_time_ecmwf"] == leadtime, era5_prob_col_name
            ]
            y_prob = df.loc[
                df["lead_time_ecmwf"] == leadtime, ecmwf_prob_col_name
            ]
            mae_list_per_threshold.append(
                metrics.mean_absolute_error(y_true, y_prob)
            )

            for threshold in threshold_list:
                y_pred = y_prob > threshold
                accuracy_list_per_threshold.append(
                    metrics.accuracy_score(y_true, y_pred)
                )
                f1_score_list_per_threshold.append(
                    metrics.f1_score(y_true, y_pred)
                )
            mae_list.append(mae_list_per_threshold)
            accuracy_list.append(accuracy_list_per_threshold)
            f1_score_list.append(f1_score_list_per_threshold)

        for col in range(3):

            if n_rows > 1:
                ax = axs[row, col]
            else:
                ax = axs[col]

            if col == 0:
                ax.plot(leadtime_list, mae_list)
                ax.set_title(
                    "Mean Absolute Error per leadtime \n (quantile = "
                    + quantile_label
                    + ")"
                )
                ax.set_ylabel("MAE")

            elif col == 1:
                for leadtime in leadtime_list:
                    ax.plot(
                        threshold_list,
                        accuracy_list[leadtime - 1],
                        label="leadtime: " + str(leadtime),
                    )
                ax.set_title(
                    "Accuracy score per leadtime and threshold value \n (quantile = "  # noqa: E501
                    + quantile_label
                    + ")"
                )
                ax.set_ylabel("Accuracy")
                ax.set_xlabel("Threshold value")
                ax.legend(loc="best")

            else:
                for leadtime in leadtime_list:
                    ax.plot(
                        threshold_list,
                        f1_score_list[leadtime - 1],
                        label="leadtime: " + str(leadtime),
                    )
                ax.set_title(
                    "F1-score per leadtime and threshold value \n (quantile = "  # noqa: E501
                    + quantile_label
                    + ")"
                )
                ax.set_ylabel("F1-score")
                ax.set_xlabel("Threshold value")
                ax.legend(loc="best")

    return


##################################################################
def plot_roc_auc_analysis(ecmwf_df, era5_df, quantile_value_list, month_range):

    if "adm_pcode" in ecmwf_df.columns.values:
        geom_id = "adm_pcode"
    else:
        geom_id = "pixel_geom_id"

    df = pd.merge(
        ecmwf_df,
        era5_df,
        on=[geom_id, "valid_time_year", "valid_time_month"],
        suffixes=["_ecmwf", "_era5"],
    )
    df = df[df["valid_time_month"].isin(month_range)]

    leadtime_list = df["lead_time_ecmwf"].unique()

    if not isinstance(quantile_value_list, list):
        quantile_value_list = [quantile_value_list]

    n_rows = len(quantile_value_list)

    fig, axs = plt.subplots(ncols=2, nrows=n_rows, figsize=(15, 6 * n_rows))

    for row in range(n_rows):

        auc_value_list = []
        quantile_value = quantile_value_list[row]
        quantile_label = "%.2f" % quantile_value
        ecmwf_prob_col_name = ("prob_q_" + quantile_label + "_ecmwf").replace(
            ".", "_"
        )
        era5_prob_col_name = ("prob_q_" + quantile_label + "_era5").replace(
            ".", "_"
        )

        for col in range(2):

            if n_rows > 1:
                ax = axs[row, col]
            else:
                ax = axs[col]

            if col == 0:

                title_text = (
                    "ROC dependecy to leadtime (quantile = "
                    + quantile_label
                    + ")"
                )

                plot_df = df[df["lead_time_ecmwf"] == 1]
                fpr, tpr, thresholds = metrics.roc_curve(
                    plot_df[era5_prob_col_name], plot_df[ecmwf_prob_col_name]
                )
                ax.plot(fpr, fpr, label="no skill baseline")

                ax.set_ylabel("True Positive Rate")
                ax.set_xlabel("False Positive Rate")

                for i in leadtime_list:
                    plot_df = df[df["lead_time_ecmwf"] == i]
                    fpr, tpr, thresholds = metrics.roc_curve(
                        plot_df[era5_prob_col_name],
                        plot_df[ecmwf_prob_col_name],
                    )
                    ax.plot(fpr, tpr, label="lead_time: " + str(i))
                    auc_value_list.append(metrics.auc(fpr, tpr))

            else:
                title_text = (
                    "Area Under the Curve per leadtime (quantile = "
                    + quantile_label
                    + ")"
                )
                ax.plot([1, 6], [0.5, 0.5], label="no skill baseline")
                ax.plot(leadtime_list, auc_value_list, label="AUC")

                ax.set_ylabel("AUC")
                ax.set_xlabel("lead time")
                ax.set_ylim([0, 1])

            ax.legend(loc="best")
            ax.set_title(title_text)

    return


##################################################################
def preparece_accuracy_map(
    ecmwf_df,
    era5_df,
    admin_df,
    quantile_value_list,
    month_range,
    leadtime,
    threshold,
    tp_col_name,
):

    if "adm_pcode" in ecmwf_df.columns.values:
        geom_id = "adm_pcode"
        column_list = [geom_id]
    else:
        geom_id = "pixel_geom_id"
        column_list = [geom_id, "latitude_ecmwf", "longitude_ecmwf"]

    column_list.append("lead_time_ecmwf")

    if not isinstance(quantile_value_list, list):
        quantile_value_list = [quantile_value_list]

    df = pd.merge(
        ecmwf_df,
        era5_df,
        on=[geom_id, "valid_time_year", "valid_time_month"],
        suffixes=["_ecmwf", "_era5"],
    )
    df = df[
        (df["valid_time_month"].isin(month_range))
        & (df["lead_time_ecmwf"] == leadtime)
    ]

    for quantile_value in quantile_value_list:
        quantile_label = "%.2f" % quantile_value
        acc_label = ("accuracy_q_" + quantile_label).replace(".", "_")
        ecmwf_prob_col_name = ("prob_q_" + quantile_label + "_ecmwf").replace(
            ".", "_"
        )
        era5_prob_col_name = ("prob_q_" + quantile_label + "_era5").replace(
            ".", "_"
        )

        df[acc_label] = (
            df[era5_prob_col_name] == (df[ecmwf_prob_col_name] > threshold) * 1
        ) * 1
        df[acc_label] = df.groupby(geom_id)[acc_label].transform("mean")
        column_list.append(acc_label)

    df = df[column_list].drop_duplicates()
    df.reset_index(drop=True, inplace=True)

    if geom_id == "adm_pcode":
        acc_map_df = gpd.GeoDataFrame(pd.merge(df, admin_df, on="adm_pcode"))
    else:
        acc_map_df = gpd.GeoDataFrame(
            df,
            geometry=gpd.points_from_xy(df.longitude_ecmwf, df.latitude_ecmwf),
            crs="EPSG:4326",
        )

    return acc_map_df


##################################################################
def plot_accuracy_map(plot_df, quantile_value_list):

    n_rows = len(quantile_value_list)

    fig, axs = plt.subplots(ncols=1, nrows=n_rows, figsize=(8, 6 * n_rows))

    for row in range(n_rows):
        ax = axs[row]

        quantile_value = quantile_value_list[row]
        quantile_label = "%.2f" % quantile_value
        acc_label = ("accuracy_q_" + quantile_label).replace(".", "_")

        plot_df.plot(column=acc_label, legend=True, cmap="OrRd", ax=ax)

        ax.set_title(
            "Accuracy score per leadtime and threshold value \n (quantile = "
            + quantile_label
            + ")"
        )

    return
