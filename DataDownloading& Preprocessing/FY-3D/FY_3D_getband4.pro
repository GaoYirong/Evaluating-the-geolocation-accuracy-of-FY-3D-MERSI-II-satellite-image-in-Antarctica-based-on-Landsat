;Through the FY Satellite Remote Sensing Data Service Website (https://satellite.nsmc.org.cn/PortalSite/Data/Satellite.aspx?currentculture=zh-CN),\
; preview images for the corresponding month and region, and confirm through visual interpretation that the images are cloud-free and in good condition.
;This program mainly extracts the band 4 data from the downloaded FY3D HDF5 files, and performs projection so that it is in the same L8 coordinate system as the original data.
pro preMERSI2_250m
  compile_opt idl2, hidden
  tic
  DLM_LOAD, 'HDF5', 'XML', 'MAP_PE', 'NATIVE'
  e = ENVI(/h)
  
  
  start_time = SYSTIME( /SECONDS )  


  ;data path
  ;data_folder_path = "FY3D_data your path";;HDF5
  ;geo_folder_path = "output FY3D_geo your path";HDF5
  
  data_folder_path = "yourpath\test_data\data";;HDF5
  geo_folder_path = "yourpath\test_data\geo";HDF5
  
  
  data_file_list = FILE_SEARCH(data_folder_path + "\*.HDF", COUNT=file_count)
  geo_file_list = FILE_SEARCH(geo_folder_path + "\*.HDF", COUNT=file_count)
  
  
  
FOR i=0, file_count-1 DO BEGIN

 
  
  fnDat = data_file_list[i]
  print,fnDat

  fnSz  = geo_file_list[i]
  print,fnSz
 


  ;flie name
  dirname = FILE_DIRNAME(fnDat)
  ;  print,dirname
  ;Extract the time information from the HDF file
  date = (FILE_BASENAME(fnDat)).Extract $
    ('20[1-4][0-9][0,1][0-9][0-3][0-9]_[0-9][0-9][0-9][0-9]')
    
  ;The name of the third output band is as follows. In this program, only the information of the four band is provided.
  refb4fn = dirname + PATH_SEP() + 'MERSI2_' + date + '_B4TOA_zenith.dat'
  ;  refb2fn = dirname + PATH_SEP() + 'MERSI2_' + date + '_B2TOA_zenith.dat'

  ;Read the array of relevant data from the hdf file of "data". Here, there is only a simple array, without any coordinate system information, etc.
  fdid = H5F_OPEN(fnDat)
  rawRefb4 = h5GetData(fdid,'Data/EV_250_RefSB_b4')
  rawRefb2 = h5GetData(fdid,'Data/EV_250_RefSB_b2')
  calCoef = h5GetData(fdid, '/Calibration/VIS_Cal_Coeff')
  dst =(h5GetAttr(fdid, 'EarthSun Distance Ratio'))[0]
  ESUN = h5GetAttr(fdid, 'Solar_Irradiance')
  tbbA = h5GetAttr(fdid, 'TBB_Trans_Coefficient_A')
  tbbB = h5GetAttr(fdid, 'TBB_Trans_Coefficient_B')
  H5F_CLOSE, fdid


  ;Read the arrays of relevant data from the geo's hdf file, such as latitude and longitude, solar zenith angle, etc.
  fsid = H5F_OPEN(fnSz)
  SolZ = FLOAT(h5GetData(fsid, 'Geolocation/SolarZenith') * !pi / 180  )
  lat = FLOAT(h5GetData(fsid, 'Geolocation/Latitude'))
  lon = FLOAT(h5GetData(fsid, 'Geolocation/Longitude'))
  H5F_CLOSE, fsid
  
  ;This step involves converting the latitude and longitude values in the array into the values of the polar projection coordinate system used in PS. 
  ;If this step is omitted, it will take a very long time to generate the GLT file by directly using the latitude and longitude data.
  in_proj = ENVI_PROJ_CREATE(/GEOGRAPHIC)
  out_proj= ENVI_PROJ_CREATE(PE_COORD_SYS_CODE=3031,TYPE=42)

  envi_convert_projection_coordinates,lon,lat,in_proj,$
    xmap,ymap,out_proj

  ;print,xmap,ymap

;  lat_TempFn = dirname + PATH_SEP() + 'MERSI2_' + date + '_lat.dat'
;  lon_TempFn = dirname + PATH_SEP() + 'MERSI2_' + date + '_lon.dat'
  
  ;;Generate grid data for longitude, latitude and solar zenith angle. Since both the longitude and latitude data and the solar zenith angle data have a resolution of 1000 meters, 
  ;this step is to prepare for subsequent resampling to a 250-meter resolution.

  SolZ_TempFn = e.GetTemporaryFilename()
  Solz_raster = e.CreateRaster(SolZ_TempFn,SolZ,INHERITS_FROM = raster)
  Solz_raster.Save
  SolZ = !null

  lat_TempFn = e.GetTemporaryFilename()
  lat_raster = e.CreateRaster(lat_TempFn,ymap,INHERITS_FROM = raster)
  lat_raster.Save
  lat = !null

  lon_TempFn = e.GetTemporaryFilename()
  lon_raster = e.CreateRaster(lon_TempFn,xmap,INHERITS_FROM = raster)
  lon_raster.Save
  lon = !null
  
  
  
  

  rw = N_elements(rawRefb4[0,*])
  cl = N_elements(rawRefb4[*,0])
  
  ;Resampling the data of solar zenith angle and longitude/latitude coordinates
  SolZ_r = ENVIResampleRaster(Solz_raster, DIMENSIONS=[cl,rw], METHOD='Bilinear')
  SolZ_r = SolZ_r.GetData(bands=0)

  lat_r = ENVIResampleRaster(lat_raster, DIMENSIONS=[cl,rw], METHOD='Bilinear')
  lat_r = lat_r.GetData(bands=0)


;  lat_TempFn2 = dirname + PATH_SEP() + 'MERSI2_' + date + '_lat_resize_idl.dat'
  lat_TempFn2 = e.GetTemporaryFilename()
  lat_raster2 = e.CreateRaster(lat_TempFn2,lat_r,INHERITS_FROM = raster)
  lat_raster2.Save
  lat_id = ENVIRasterToFID(lat_raster2)



  lon_r = ENVIResampleRaster(lon_raster, DIMENSIONS=[cl,rw], METHOD='Bilinear')
  lon_r = lon_r.GetData(bands=0)

;  lon_TempFn2 = dirname + PATH_SEP() + 'MERSI2_' + date + '_lon_resize_idl.dat'
  lon_TempFn2 = e.GetTemporaryFilename()
  lon_raster2 = e.CreateRaster(lon_TempFn2,lon_r,INHERITS_FROM = raster)
  lon_raster2.Save
  lon_id = ENVIRasterToFID(lon_raster2)


  ;RawBand4 data from DN value calibration to TOA
  refb4 = MAKE_ARRAY([cl,rw], type = 5)
  ;Divide by 100.
  print,calCoef[1,3]
  print,calCoef[0,3]
  refb4= (rawRefb4 * calCoef[1,3] + calCoef[0,3])/100 * (dst^2) / cos(SolZ_r)

  ;  refb3= (rawRefb3 * calCoef[1,2] + calCoef[0,2])/100
  rawRefb4 = !null
  SolZ_r = !null
  lon_r = !null
  lat_r = !null

  Solz_raster.Close


  ;Generate raster data for band4_TOA after calibration
  refb4_Tempfn =  e.GetTemporaryFilename()
  refb4_raster = e.CreateRaster(refb4_Tempfn,refb4,INHERITS_FROM = raster)
  refb4_raster.Save
  refb4_id = ENVIRasterToFID(refb4_raster)
  ENVI_FILE_QUERY,refb4_id, DIMS = ref_dims
  refb4 = !null




;  GLTfn = ENVI_PICKFILE(title = 'select GLT file')
;  ENVI_OPEN_FILE,GLTfn,R_FID = GLT_id
  
  ;Preparation for generating GLT, set the coordinate system of input and output, here are ps polar projection coordinate system 
  in_proj2 = ENVI_PROJ_CREATE(PE_COORD_SYS_CODE=3031,TYPE=42)
  out_proj2= ENVI_PROJ_CREATE(PE_COORD_SYS_CODE=3031,TYPE=42)
;  gltTempFn = dirname + PATH_SEP() + 'MERSI2_' + date + '_GLT.dat'
;  gltTempFn = dirname + PATH_SEP() + 'MERSI2_' + date + '_GLT'
;  gltTempFn = e.GetTemporaryFilename()
  gltTempFn = 'yourpath\test_data\glt\'+date+'_GLT.dat'
  print,gltTempFn
  ;enerate a GLT file using latitude/longitude data from the resampled data
  ENVI_DOIT, 'ENVI_GLT_DOIT', DIMS = ref_dims, $
      I_PROJ = in_proj2,  O_PROJ = out_proj2, $
      OUT_NAME = gltTempFn, $
      PIXEL_SIZE = 250.0, $
      R_FID = GLT_id, ROTATION = 0 , $
      X_FID = lon_id, X_POS = [0], $
      Y_FID = lat_id, Y_POS = [0]
  


  ;Geometry correction of Band3_TOA file using the generated GLT file, i.e. giving coordinate system information
  ENVI_DOIT,'ENVI_GEOREF_FROM_GLT_DOIT', $
    BACKGROUND = 0, $
    FID = refb4_id, $
    GLT_FID = GLT_id, $
    OUT_NAME = refb4fn, $
    pos = [0:0]



  refb4_raster.Close
  lat_raster.Close
  lon_raster.Close
  lat_raster2.Close
  lon_raster2.Close

  ;Calculate the processing time for each file, roughly 15-20 min
  elapsed_time = SYSTIME( /SECONDS ) - start_time ; 
  print, "first",i+1,"documents have been processed.","time", elapsed_time, "s"



ENDFOR
  

  toc
end

function h5GetData, fid, str
  compile_opt idl2, hidden

  str_id = H5D_OPEN(fid, str)
  slope = FLOAT(h5GetAttr(str_id, 'Slope'))
  intercept = FLOAT(h5GetAttr(str_id, 'Intercept'))
  data = FLOAT(H5D_READ(str_id))
  foreach _slope, slope, index do $
    data[*, *, index] = _slope * data[*, *, index] + intercept[index]
  H5D_CLOSE, str_id

  RETURN, data
end

function h5GetAttr, fid, str
  compile_opt idl2, hidden

  str_id = H5A_OPEN_NAME(fid, str)
  attr = H5A_READ(str_id)
  H5A_CLOSE, str_id

  RETURN, attr
end
