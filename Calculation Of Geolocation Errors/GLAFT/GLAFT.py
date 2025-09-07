import os
import numpy as np
import rasterio
import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import glaft

# --- 1. parameter settings ---
try:
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['xtick.labelsize'] = 20
    plt.rcParams['ytick.labelsize'] = 20
    plt.rcParams['legend.fontsize'] = 12
    plt.rcParams['axes.titlesize'] = 24
except Exception as e:
    print(f"Warning: Failed to set Times New Roman font. Using default font. Error: {e}")

# --- 2.  file paths---
vx_folder = 'G:\\FY-3D_geo_arruary\\2019_2024Amery\\GLAFT_displacement\\GLAFT_displacement_vx'
vy_folder = 'G:\\FY-3D_geo_arruary\\2019_2024Amery\\GLAFT_displacement\\GLAFT_displacement_vy'
static_area = 'G:\\FY-3D_geo_arruary\\2019_2024Amery\\roi\\amery_bedrock_roi.shp'
output_plot_folder = 'G:\\FY-3D_geo_arruary\\2019_2024Amery\\analysis_plots'
os.makedirs(output_plot_folder, exist_ok=True)

vx_files = sorted([os.path.join(vx_folder, f) for f in os.listdir(vx_folder) if f.endswith('.tif')])
vy_files = sorted([os.path.join(vy_folder, f) for f in os.listdir(vy_folder) if f.endswith('.tif')])

if len(vx_files) != len(vy_files):
    raise ValueError("Number of VX and VY files do not match!")

results = []

# --- 3. Iterate through files and perform analysis and plotting---
for vx_path, vy_path in zip(vx_files, vy_files):
    print("-" * 50)
    print(f"Processing: {os.path.basename(vx_path)} 和 {os.path.basename(vy_path)}")

    try:
        experiment = glaft.Velocity(vxfile=vx_path, vyfile=vy_path, static_area=static_area)
        experiment.static_terrain_analysis()

        delta_x = experiment.metric_static_terrain_x
        delta_y = experiment.metric_static_terrain_y
        outlier_percent = 100 * experiment.outlier_percent

        print(f'  Delta_x: {delta_x:.4f} (m)')
        print(f'  Delta_y: {delta_y:.4f} (m)')
        print(f'  KDE peak position x: {experiment.kdepeak_x:.4f} (m)')
        print(f'  KDE peak position y: {experiment.kdepeak_y:.4f} (m)')
        print(f'  Mismatch percentage: {outlier_percent:.2f}%')

        results.append({
            'VX File': os.path.basename(vx_path),
            'VY File': os.path.basename(vy_path),
            'Delta X (m)': delta_x,
            'Delta Y (m)': delta_y,
            'Error Percentage (%)': outlier_percent
        })

        # --- 4. Create subplots and plot ---
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

        # Plot full extent on the first subplot (ax1)
        experiment.static_terrain_analysis(plot='full', ax=ax1)
        ax1.set_title('(a) Full Extent', loc='left', fontweight='bold', x=0.03, y=0.93)

        # Plot zoomed extent on the second subplot (ax2)
        experiment.plot_zoomed_extent(metric=1, ax=ax2)
        ax2.set_title('(b) Zoomed Extent', loc='left', fontweight='bold', x=0.03, y=0.93)

        # --- [Newly Added Code] Add point and annotation at KDE peak position ---

        # Get KDE peak coordinates
        kde_x = experiment.kdepeak_x
        kde_y = experiment.kdepeak_y

        # 1. Draw a prominent marker at the peak position (e.g., a red cross)
        ax2.plot(kde_x, kde_y, 'r+', markersize=12, mew=2, label='KDE Peak')

        # 2. Add annotation text near the marker
        ax2.annotate(
            f'KDE Peak:\n({kde_x:.2f}, {kde_y:.2f})',
            xy=(kde_x, kde_y),
            xytext=(15, 15),
            textcoords='offset points',
            ha='left',
            va='bottom',
            fontsize=18,
            bbox=dict(boxstyle='round,pad=0.4', fc='yellow', alpha=0.7),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2', color='black')
        )




        plt.tight_layout(pad=2.0)


        base_name = os.path.splitext(os.path.basename(vx_path))[0].replace('_vx', '')
        plot_output_path = os.path.join(output_plot_folder, f"{base_name}_analysis.png")
        plt.savefig(plot_output_path, dpi=300, bbox_inches='tight')
        print(f"  图像已保存至: {plot_output_path}")
        plt.close(fig)

    except Exception as e:
        print(f"  处理文件 {os.path.basename(vx_path)} 时发生错误: {e}")

# --- 6. Save results to Excel file  ---
df = pd.DataFrame(results)
excel_path = 'G:\\FY-3D_geo_arruary\\2019_2024Amery\\analysis_results.xlsx'
df.to_excel(excel_path, index=False)

print("-" * 50)
print(f"All analyses completed! Results saved to: {excel_path}")