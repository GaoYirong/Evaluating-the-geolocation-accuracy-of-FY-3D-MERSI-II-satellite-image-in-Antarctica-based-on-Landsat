import os
import h5py
import numpy as np
import pandas as pd
import pyproj

# Folder path
folder_path = r"yourpath\DataDownloading_Preprocessing\FY-3D\test_data\geo"

# Initialize projection transformers (EPSG:4326 to EPSG:3031)
proj_wgs84 = pyproj.Proj(init='epsg:4326')  # WGS84 geographic coordinate system
proj_epsg3031 = pyproj.Proj(init='epsg:3031')  # EPSG:3031 polar stereographic projection

# Find HDF files and sort by filename
hdf_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.HDF')])
print("Number of HDF files found:", len(hdf_files))
if len(hdf_files) == 0:
    print("No HDF files found in the folder.")
    exit()

# Create an empty DataFrame to store results
results_df = pd.DataFrame(columns=[
    'filename', 'heading_angle',
    'start_latitude', 'start_longitude', 'end_latitude', 'end_longitude',
    'start_x', 'start_y', 'end_x', 'end_y'
])

# Process each HDF file
for file_name in hdf_files:
    # Construct full file path
    file_path = os.path.join(folder_path, file_name)

    print(f"Processing file: {file_name}")

    # Read HDF file
    with h5py.File(file_path, 'r') as file:
        # Access 'Latitude' and 'Longitude' datasets under 'Geolocation' group
        latitude = file['Geolocation']['Latitude'][:]
        longitude = file['Geolocation']['Longitude'][:]

    # Calculate number of columns
    num_cols = latitude.shape[1]

    # Determine center pixel indices for start/end positions
    start_index = num_cols // 2
    end_index = start_index + 1

    # Calculate start/end coordinates (average of center pixels)
    start_latitude = (latitude[0, start_index] + latitude[0, start_index + 1]) / 2
    start_longitude = (longitude[0, start_index] + longitude[0, start_index + 1]) / 2
    end_latitude = (latitude[-1, start_index] + latitude[-1, start_index + 1]) / 2
    end_longitude = (longitude[-1, start_index] + longitude[-1, start_index + 1]) / 2

    # Method 1: Calculate heading angle (using projected coordinates)
    # Convert geographic coordinates to EPSG:3031
    start_x, start_y = pyproj.transform(proj_wgs84, proj_epsg3031, start_longitude, start_latitude)
    end_x, end_y = pyproj.transform(proj_wgs84, proj_epsg3031, end_longitude, end_latitude)

    # Calculate coordinate differences
    delta_x = end_x - start_x
    delta_y = end_y - start_y

    # Compute heading angle (radians)
    bearing1 = np.arctan2(delta_x, delta_y)

    # Convert radians to degrees
    bearing1_deg = np.degrees(bearing1)

    # Normalize angle to 0-360° range
    if bearing1_deg < 0:
        bearing1_deg += 360

    # Add results to DataFrame
    results_df = results_df.append({
        'filename': file_name, 'heading_angle': bearing1_deg,
        'start_latitude': start_latitude, 'start_longitude': start_longitude,
        'end_latitude': end_latitude, 'end_longitude': end_longitude,
        'start_x': start_x, 'start_y': start_y, 'end_x': end_x, 'end_y': end_y
    }, ignore_index=True)

# Save results to Excel
excel_file_path = os.path.join(folder_path, 'Ameryheading_angle.xlsx')
results_df.to_excel(excel_file_path, index=False)

print("Heading angle results saved to:", excel_file_path)