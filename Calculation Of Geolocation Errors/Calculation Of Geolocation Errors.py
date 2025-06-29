import os
import numpy as np
from osgeo import gdal
import pandas as pd
from sklearn.ensemble import IsolationForest
def rmse(array):
    """Calculate Root Mean Square Error (RMSE)"""
    return np.sqrt(np.mean(array ** 2))


# Calculate NRMSE: https://blog.51cto.com/u_16175504/12287083
def nrmse(band):
    rmse = np.sqrt(np.nanmean(band ** 2))  # Calculate RMSE
    range_band = np.nanmax(band) - np.nanmin(band)  # Calculate data range
    return rmse / range_band if range_band != 0 else np.nan  # Calculate NRMSE, avoid division by zero


def count_values(result):
    """Count number and proportion of pixels in different value ranges"""
    counts = [np.sum(result < -1000), np.sum((result >= -1000) & (result < -500)),
              np.sum((result >= -500) & (result < -250)), np.sum((result >= -250) & (result < 0)),
              np.sum((result >= 0) & (result < 250)), np.sum((result >= 250) & (result < 500)),
              np.sum((result >= 500) & (result < 1000)), np.sum(result >= 1000)]
    total_pixels = np.prod(result.shape)
    proportions = [count / total_pixels for count in counts]
    return counts, proportions


def clean_data(array):
    # Define reasonable min/max values based on data characteristics
    reasonable_min_value = -65536
    reasonable_max_value = 65536

    # Replace extreme values with NaN
    array[array > reasonable_max_value] = np.nan
    array[array < reasonable_min_value] = np.nan

    # Handle infinity values
    array[array == np.inf] = np.finfo(np.float64).max
    array[array == -np.inf] = np.finfo(np.float64).min

    # Remove NaN values
    array = array[~np.isnan(array)]

    return array


# Isolation Forest parameters
isolation_forest_params = {
    'n_estimators': 130,
    'max_samples': 256,
    'contamination': 0.3
}


def outlier_filter(result):
    """Apply Isolation Forest for outlier filtering"""
    result = clean_data(result)

    # Flatten data for processing
    flattened_result = result.reshape(-1, 1)

    # Create and configure Isolation Forest model
    model = IsolationForest(**isolation_forest_params)

    # Train model
    model.fit(flattened_result)

    # Predict outliers
    outliers = model.predict(flattened_result)

    # Reshape to match original dimensions
    outliers = outliers.reshape(result.shape)

    # Replace outliers with NaN
    filtered_result = np.where(outliers == -1, np.nan, result)

    return filtered_result


def rmse_zero(band):
    """Calculate RMSE with 0 as true value"""
    return np.sqrt(np.nanmean(band ** 2))


def process_band(band):
    """Process a single band"""
    print("NRMSE:", nrmse(band))

    # Pre-filter statistics
    counts_before, proportions_before = count_values(band)
    bias_before = np.nanmean(band)
    std_dev_before = np.nanstd(band)
    abs_mean_before = np.nanmean(np.abs(band))
    rmse_before = rmse_zero(band)

    # Filter processing
    band[band > 1500] = np.nan
    filtered_result = outlier_filter(band)

    # Post-filter statistics
    counts_after, proportions_after = count_values(filtered_result)
    bias_after = np.nanmean(filtered_result)
    std_dev_after = np.nanstd(filtered_result)
    abs_mean_after = np.nanmean(np.abs(filtered_result))
    rmse_after = rmse_zero(filtered_result)

    return (filtered_result, counts_before, proportions_before, bias_before,
            std_dev_before, abs_mean_before, rmse_before, counts_after,
            proportions_after, bias_after, std_dev_after, abs_mean_after, rmse_after)


def process_tiff(input_tiff):
    """Process a single TIFF file"""
    # Load heading angle data from Excel
    heading_excel_path = r"G:\github\Calculation_indicators\heading_angle\Ameryheading_angle.xlsx"
    heading_df = pd.read_excel(heading_excel_path)

    # Extract timestamp from filename (e.g., 20190106_1325)
    tiff_name = os.path.basename(input_tiff)
    time_key = "_".join(tiff_name.split("_")[:2])  # Format: YYYYMMDD_HHMM

    # Match heading angle using timestamp
    heading_row = heading_df[heading_df['filename'].str.contains(time_key, regex=False)]
    if heading_row.empty:
        print(f"Warning: No heading angle found for {tiff_name}, skipping...")
        return None

    # Extract and convert heading angle to radians
    heading_angle = np.radians(heading_row['heading_angle'].iloc[0])

    # Load TIFF data
    dataset = gdal.Open(input_tiff)
    if dataset is None:
        print(f"Failed to open {input_tiff}")
        return

    band1 = dataset.GetRasterBand(1).ReadAsArray().astype(float)
    band2 = dataset.GetRasterBand(2).ReadAsArray().astype(float)

    band1 = clean_data(band1)
    band2 = clean_data(band2)

    geotransform = dataset.GetGeoTransform()
    projection = dataset.GetProjection()
    dataset = None  # Release resources

    # Process band1
    (filter_band1, counts_before_band1, proportions_before_band1, bias_before_band1,
     std_dev_before_band1, abs_mean_before_band1, rmse_before_band1, counts_after_band1,
     proportions_after_band1, bias_after_band1, std_dev_after_band1, abs_mean_after_band1,
     rmse_after_band1) = process_band(band1)

    # Process band2
    (filter_band2, counts_before_band2, proportions_before_band2, bias_before_band2,
     std_dev_before_band2, abs_mean_before_band2, rmse_before_band2, counts_after_band2,
     proportions_after_band2, bias_after_band2, std_dev_after_band2, abs_mean_after_band2,
     rmse_after_band2) = process_band(band2)

    # Align array lengths
    min_length = min(len(filter_band1), len(filter_band2))
    filter_band1 = filter_band1[:min_length]
    filter_band2 = filter_band2[:min_length]

    # Calculate along-track and cross-track components
    band_along = filter_band2 * np.cos(heading_angle) + filter_band1 * np.sin(heading_angle)
    band_cross = filter_band2 * np.sin(heading_angle) - filter_band1 * np.cos(heading_angle)

    # Process along-track band
    (_, counts_along, proportions_along, bias_along, std_dev_along, abs_mean_along,
     rmse_along, *_) = process_band(band_along)

    # Process cross-track band
    (_, counts_cross, proportions_cross, bias_cross, std_dev_cross, abs_mean_cross,
     rmse_cross, *_) = process_band(band_cross)

    # Return all statistics
    return [
        # band1 results
        counts_before_band1, proportions_before_band1, bias_before_band1, std_dev_before_band1,
        abs_mean_before_band1, rmse_before_band1, counts_after_band1, proportions_after_band1,
        bias_after_band1, std_dev_after_band1, abs_mean_after_band1, rmse_after_band1,
        # band2 results
        counts_before_band2, proportions_before_band2, bias_before_band2, std_dev_before_band2,
        abs_mean_before_band2, rmse_before_band2, counts_after_band2, proportions_after_band2,
        bias_after_band2, std_dev_after_band2, abs_mean_after_band2, rmse_after_band2,
        # band_along results
        counts_along, proportions_along, bias_along, std_dev_along, abs_mean_along, rmse_along,
        # band_cross results
        counts_cross, proportions_cross, bias_cross, std_dev_cross, abs_mean_cross, rmse_cross,
    ]


def process_folder(input_folder, output_folder):
    """Process all TIFF files in a folder"""
    stats_data_band1 = []
    stats_data_band2 = []
    stats_data_bandalong = []
    stats_data_bandcross = []

    for file in os.listdir(input_folder):
        if file.lower().endswith(('.tif', '.tiff')):
            input_tiff = os.path.join(input_folder, file)
            results = process_tiff(input_tiff)
            if results is None:
                continue

            # Unpack results
            (cb1, pb1, bb1, sdb1, amb1, rmb1, ca1, pa1, ba1, sda1, ama1, rma1,
             cb2, pb2, bb2, sdb2, amb2, rmb2, ca2, pa2, ba2, sda2, ama2, rma2,
             cal, pal, bal, sdal, amal, rmal,
             ccr, pcr, bcr, sdcr, amcr, rmcr) = results

            # Organize statistics by band
            stats_data_band1.append(
                [file, *cb1, *pb1, bb1, sdb1, amb1, rmb1, *ca1, *pa1, ba1, sda1, ama1, rma1])
            stats_data_band2.append(
                [file, *cb2, *pb2, bb2, sdb2, amb2, rmb2, *ca2, *pa2, ba2, sda2, ama2, rma2])
            stats_data_bandalong.append(
                [file, *cal, *pal, bal, sdal, amal, rmal])
            stats_data_bandcross.append(
                [file, *ccr, *pcr, bcr, sdcr, amcr, rmcr])

    # Create DataFrames
    column_names = ["File", "Before -1000+", "Before -1000 to -500", "Before -500 to -250",
                    "Before -250 to 0", "Before 0-250", "Before 250-500", "Before 500-1000",
                    "Before 1000+", "Before Prop -1000+", "Before Prop -1000 to -500",
                    "Before Prop -500 to -250", "Before Prop -250 to 0", "Before Prop 0-250",
                    "Before Prop 250-500", "Before Prop 500-1000", "Before Prop 1000+",
                    "Bias Before", "Std Dev Before", "Abs Mean Before", "RMSE Before"]

    # Additional columns for band1/band2 (post-filtering)
    post_cols = ["After -1000+", "After -1000 to -500", "After -500 to -250",
                 "After -250 to 0", "After 0-250", "After 250-500", "After 500-1000",
                 "After 1000+", "After Prop -1000+", "After Prop -1000 to -500",
                 "After Prop -500 to -250", "After Prop -250 to 0", "After Prop 0-250",
                 "After Prop 250-500", "After Prop 500-1000", "After Prop 1000+",
                 "Bias After", "Std Dev After", "Abs Mean After", "RMSE After"]

    # Create DataFrames with appropriate columns
    df_band1 = pd.DataFrame(stats_data_band1, columns=column_names + post_cols)
    df_band2 = pd.DataFrame(stats_data_band2, columns=column_names + post_cols)
    df_bandalong = pd.DataFrame(stats_data_bandalong, columns=column_names)
    df_bandcross = pd.DataFrame(stats_data_bandcross, columns=column_names)

    # Save results to Excel
    output_excel_band1 = os.path.join(output_folder, "stats_band1_bedrock.xlsx")
    output_excel_band2 = os.path.join(output_folder, "stats_band2_bedrock.xlsx")
    output_excel_along = os.path.join(output_folder, "stats_along_bedrock.xlsx")
    output_excel_cross = os.path.join(output_folder, "stats_cross_bedrock.xlsx")

    df_band1.to_excel(output_excel_band1, index=False)
    df_band2.to_excel(output_excel_band2, index=False)
    df_bandalong.to_excel(output_excel_along, index=False)
    df_bandcross.to_excel(output_excel_cross, index=False)


# Main processing
input_folder =r"G:\github\Displacement\bedrock_clip\clip_bedrock_roi"
output_folder =r"G:\github\Calculation_indicators"

# Execute processing pipeline
process_folder(input_folder, output_folder)