'''
#Originally Developed in FORTRAN by Dr. Mohammad Al-Hamdan  
#USRA at NASA/MSFC
#Converted into Python by Erica Burrows (2016)
#Modified by Dr. Muhammad Barik (2017) for regional analysis.
#Modified by Ching An Yang and Shane Coffield (2017)
#Modified by Dr. Muhammad Barik (2018) 
#Modified by Anna Boser (2020)
#Purpose: Extract MAIAC AOD Data from HDF Files in San Francisco Bay
'''

#this script resample MODIS MAIAC data based defined grid values

import os
import gdal
import numpy as np
import time
import pandas as pd
import glob 




start = time.time()

lonmin = -123.5
lonmax = -120.8
latmax = 39
latmin = 36.8


MAIAC_path = r'~/Documents/GitHub/PM_prediction/Data/Raw/MAIAC' #MAIAC file folder
output_path=r'~/Documents/GitHub/PM_prediction/Data/Processed/AOD' #output folder 

#list and read MAIAC files 
files = os.listdir(MAIAC_path) 
#files = [f for f in files if f[5] == "A" and f[6:9] == 'AOT' and f[-3:]=='hdf']
count = 0
print('Reading MAIAC input files...')
for f in files:
    count+=1
    print ('Running file {} of {}'.format(count, len(files)))
    dayfname = f[14:16]         #determining the day of each file
    print ('DOY '+str(dayfname))
    hdf_file = gdal.Open(MAIAC_path + f)    
    print (f)
    subDatasets = hdf_file.GetSubDatasets() #locating the keys of the subdatasets
    latlon_path = r'/Volumes/F/CAARE_2017/Yang/MAIAC_2016/latlon/MAIACLatlon.h01v04.hdf'
    hdf_latlon_file =gdal.Open(latlon_path)
    subDatasets_latlon = hdf_latlon_file.GetSubDatasets()
                       
    lat_key = 'HDF4_EOS:EOS_GRID:"{}":latlon:lat'.format(latlon_path)
    lon_key = 'HDF4_EOS:EOS_GRID:"{}":latlon:lon'.format(latlon_path)
    AOD_key = 'HDF4_EOS:EOS_GRID:"{}":grid1km:Optical_Depth_055'.format(MAIAC_path + f) #you only want the .55 band
                
    lat = gdal.Open(lat_key).ReadAsArray().flatten()
    lon = gdal.Open(lon_key).ReadAsArray().flatten()
    AOD = gdal.Open(AOD_key).ReadAsArray().flatten()
                        
    AOD = AOD.astype('float')
    AOD[AOD == -28672] = np.nan # -28672 represents a missing value
    print(len(AOD))
    AOD = AOD * 0.001 #scale factor provided by HDF view app
    conditions = (AOD>-9.9, lonmin<lon, lon<lonmax, latmin<lat, lat<latmax)
    indices = np.where(np.logical_and.reduce(conditions))
    #print(indices)
    temp_cols = ['lon','lat','AOD']
    #MAIAC_temp=[]
    MAIAC_temp = pd.DataFrame(columns=temp_cols)
    MAIAC_temp['lon'] = lon[indices]
    MAIAC_temp['lat'] = lat[indices]
    MAIAC_temp['AOD'] = AOD[indices]
    print(len(MAIAC_temp['AOD']))
    #print (MAIAC_temp)
    MAIAC_temp=MAIAC_temp.round(6)
    outputfile=output_path+'/MAIAC_{}'.format(dayfname)+'.txt'


print ('Done! Total time taken to run: ', time.time() - start)
