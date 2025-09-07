# Evaluating the Geolocation Accuracy of FY-3D MERSI-II Satellite Images in Antarctica Based on Landsat 8-OLI Reference Imagery

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

---

## Table of Contents

- [Project Structure](#project-structure)  
- [DataDownloading&Preprocessing](#datadownloadingpreprocessing)  
  - [Landsat 8 OLI](#landsat-8-oli-data)  
  - [FY-3D MERSI-II](#fy-3d-mersi-ii-data)  
- [Displacement Extraction](#displacement-extraction)  
- [Calculation Of Geolocation Errors](#calculation-of-geolocation-errors)  
- [Figures](#figures)  
- [Data Description](#data-description)  
- [External Resources](#external-resources)  
- [Notes](#notes)  
- [Contact](#contact)  
---

## Project Structure

This project is organized into three main components:

1. **Data Downloading&Preprocessing**  
2. **Displacement Extraction**  
3. **Calculation Of Geolocation Errors**
4. **Figures**
5. **Data**
---
## Data Downloading&Preprocessing

### Landsat 8 OLI Data

- Landsat 8 OLI (TOA Band 4) scenes are downloaded and composited using [Google Earth Engine (GEE)](https://earthengine.google.com/).
- The script used for compositing is included in [`GEE_code.txt`](https://github.com/GaoYirong/Evaluating-the-geolocation-accuracy-of-FY-3D-MERSI-II-satellite-image-in-Antarctica-based-on-Landsat/tree/master/DataDownloading%26%20Preprocessing/Landsat8).

### FY-3D MERSI-II Data

- FY-3D MERSI-II images are obtained from the [the National Satellite Meteorological Center(NSMC)](https://satellite.nsmc.org.cn/PortalSite/Data/Satellite.aspx?currentculture=zh-CN).
- Preprocessing steps:
  - Radiometric calibration and band extraction via IDL:[`FY_3D_getband4.pro`](https://github.com/GaoYirong/Evaluating-the-geolocation-accuracy-of-FY-3D-MERSI-II-satellite-image-in-Antarctica-based-on-Landsat/tree/master/DataDownloading%26%20Preprocessing/FY-3D).
  - Conversion from `.dat` to `.tif`: [`dat_to_tif.pro`](https://github.com/GaoYirong/Evaluating-the-geolocation-accuracy-of-FY-3D-MERSI-II-satellite-image-in-Antarctica-based-on-Landsat/tree/master/DataDownloading%26%20Preprocessing/FY-3D).
  - Projection and spatial clipping with ArcPy: [`arcpy_clip_code.txt` ](https://github.com/GaoYirong/Evaluating-the-geolocation-accuracy-of-FY-3D-MERSI-II-satellite-image-in-Antarctica-based-on-Landsat/tree/master/DataDownloading%26%20Preprocessing/FY-3D), to match the Landsat 8 reference imagery.

> The clipped extent should match or slightly fall within the corresponding Landsat 8 scene.

---

## Displacement Extraction

- Displacement fields are generated using the [COSI-Corr](http://www.tectonics.caltech.edu/slip_history/spot_coseis/) software package.
- Under the assumption that displacement over stable bedrock reflects geolocation error, only displacements within bedrock regions are used.
- Bedrock masks are obtained from the [BAS Antarctic Rock Outcrop Dataset](https://data.bas.ac.uk/items/178ec50d-1ffb-42a4-a4a3-1145419da2bb/).
- Scripts used for region clipping and masking are provided in[`clip_bedrock_roi_code.txt`](https://github.com/GaoYirong/Evaluating-the-geolocation-accuracy-of-FY-3D-MERSI-II-satellite-image-in-Antarctica-based-on-Landsat/tree/master/Displacement%20Extraction/bedrock_clip).

---

## Calculation Of Geolocation Errors

- Displacement statistics are computed using the script `Calculation Of Geolocation Errors.py`, including:
  - RMSE in x/y direction
  - Mean absolute bias (MAB)
  - Temporal and spatial distribution metrics
  - Heading angle calculations
  - Using GLAFT tool visualization [GLAFT Toolkit](https://github.com/ncu-cryosensing/GLAFT).
  - 
**Reference**:  
Zheng, W., et al. (2022). *GLAcier Feature Tracking testkit (GLAFT): a statistically and physically based framework for evaluating glacier velocity products derived from optical satellite image feature tracking*. TC, 17, 4063–4078, 2023.  
[https://doi.org/10.5194/tc-17-4063-2023](https://doi.org/10.5194/tc-17-4063-2023)

---

## Figures

This folder contains all the figures included in the paper, and the scripts used to generate them:

- `Temporal and distributional analysis.py`  
- `histogram.py`  
- `MAB.py`  
- `mk_trend_analysis.m`  

---

## Data Description

The `/Data` folder includes all processed datasets used in the analysis:

- Preprocessed **FY-3D** and **Landsat 8** images for four study regions:  
  - *Amery Ice Shelf*  
  - *Antarctic Peninsula*  
  - *Queen Maud Land*  
  - *Ross Island*

- `/Displacement/`: Displacement results from COSI-Corr for different years and regions.
- `/BedRockDisplacement/`: Extracted displacement results over bedrock areas only.
- `/Table/`: Geolocation error summary tables calculated by `Calculation Of Geolocation Errors.py`.

---

## External Resources

| Description | Link |
|------------|------|
| FY-3D MERSI-II Data Source | [NSMC Satellite Data Center](https://satellite.nsmc.org.cn/PortalSite/Data/Satellite.aspx?currentculture=zh-CN) |
| Landsat 8 Data | [Google Earth Engine](https://earthengine.google.com/) |
| Antarctic Rock Outcrop Dataset | [British Antarctic Survey (BAS)](https://data.bas.ac.uk/items/178ec50d-1ffb-42a4-a4a3-1145419da2bb/) |
| COSI-Corr Software | [Caltech Tectonics Observatory](http://www.tectonics.caltech.edu/slip_history/spot_coseis/) |
| GLAFT Toolkit | [GitHub - GLAFT](https://github.com/ncu-cryosensing/GLAFT) |

---

## Notes

- Scripts are written in **Python**, **IDL**, and **ArcPy**, and partially executed in **ENVI**.
- Python version ≥ 3.8 is recommended.
- ENVI version ≥ 5.3 is required for image display and manual checks.
- Access to Google Earth Engine requires registration.

---

## Contact

If you have any questions, suggestions, or would like to collaborate, please open an issue or contact the maintainer of this repository.

---

_Last updated: June 2025_
