;; Convert the .dat format file processed by FY_3D_getband4 into .tif format and extract the offset values.
pro dat_to_tif
  envi = ENVI(/headless)  

  dat_dir = 'yourpath\\Data Downloading and Preprocessing\\FY-3D\\test_data\\output_glt\\'
  tif_dir = 'yourpath\\Data Downloading and Preprocessing\\FY-3D\\test_data\\tif\\'
  
  
  file = file_search(dat_dir, '*.dat', count=num)
  
  for i = 0, num-1 do begin
    raster = envi.OpenRaster(file[i])
    parts = strsplit(file[i], path_sep(), /extract)
    base = strsplit(parts[-1], '.', /extract)
    tif_path = tif_dir + base[0] + '.tif'
    raster.Export, tif_path, 'TIFF'
    raster.close
  endfor
  
  print, 'Conversion completed. ', num, ' files processed.'
end