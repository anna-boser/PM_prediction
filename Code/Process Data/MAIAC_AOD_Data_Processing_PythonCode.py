'''
#Originally Developed in FORTRAN by Dr. Mohammad Al-Hamdan  
#USRA at NASA/MSFC
#Converted into Python by Erica Burrows (2016)
#Modified by Dr. Muhammad Barik (2017) for regional analysis.
#Modified by Ching An Yang and Shane Coffield (2017)
#Modified by Dr. Muhammad Barik (2018) 
#Modified by Anna Boser (2020)
#Purpose: Extract MAIAC AOD Data from HDF Files based on EPA Regions
'''

# the LatLon file comes from https://portal.nccs.nasa.gov/datashare/maiac/DataRelease/NorthAmerica/

#this script resample MODIS MAIAC data based defined grid values

import os
import gdal
import numpy as n
import time
import pandas as pd
import glob 

# region = 'ACAL' #input('Enter selected area name: ')
#region = 'Region1'
#inc = float(raw_input('What is the Radius of Your Study Area in Decimal Degrees: '))
# inc = 0.0117
#band = raw_input('Which band would you like to use (0.47/0.55/0.66/avg)?: ')
# band = '0.55'

#USER: CHANGE/ADD YEARS AND PRODUCTS BASED ON YOUR PROJECT
years = ['2017']
products = ['DarkTarget Aqua V5.1 10km'] # ?????



start = time.time()

df=pd.read_csv("~/GitHub/PM_prediction/Data/fishnet/fishnet_centroids_LatLon.csv")

#df=df.iloc[0:10000,:] #just for testing 

lonmin = df.min(axis=None)[1]
lonmax = df.max(axis=None)[1]
latmax = df.max(axis=None)[2]
latmin = df.min(axis=None)[2]


for product in products:
    i=product.strip().split(' ')
    alg = i[0]      #algorithm, DarkTarget or DeepBlue
    sat = i[1]      #satellite, Aqua or Terra
    vers = i[2]     #version, V5.1 or V6
    res = i[3][:-2] #spatial resolution, 3 or 10

    for year in years:
        MAIAC_path = r'~/GitHub/PM_prediction/Data/MAIAC' #MAIAC file folder
        output_path=r'~/GitHub/PM_prediction/Data/Variables/AOD' #output folder 
        
        print('----------------------------------------------------------')
        print('Deleting all the existing files in the output folder.')
        print('----------------------------------------------------------')
        
        existing_files = glob.glob('~/GitHub/PM_prediction/Data/Processed/AOD')
        for ef in existing_files:
            os.remove(ef)

        #list and read MAIAC files 
        files = os.listdir(MAIAC_path) 
        files = [f for f in files if f[1:7] == 'MCD19A2' and f[-3:]=='hdf']
        count = 0
        print('Reading MAIAC input files...')
        for f in files:
            count+=1
            print ('Running file {} of {} ({})'.format(count, len(files), year))
            dayfname = f[14:16]         #determining the day of each file
            print ('DOY '+str(dayfname))
            hdf_file = gdal.Open(MAIAC_path + f)    
            print (f)
            subDatasets = hdf_file.GetSubDatasets() #locating the keys of the subdatasets
            latlon_path = r'~/GitHub/PM_prediction/Data/MAIAC/latlon/MAIACLatlon.h08v05.hdf'
            hdf_latlon_file =gdal.Open(latlon_path)
            subDatasets_latlon = hdf_latlon_file.GetSubDatasets()
                       
            lat_key = 'HDF4_EOS:EOS_GRID:"{}":latlon:lat'.format(latlon_path)
            lon_key = 'HDF4_EOS:EOS_GRID:"{}":latlon:lon'.format(latlon_path)
            AOD_key = 'HDF4_EOS:EOS_GRID:"{}":grid1km:Optical_Depth_055'.format(MAIAC_path + f)
                
            lat = gdal.Open(lat_key).ReadAsArray().flatten()
            lon = gdal.Open(lon_key).ReadAsArray().flatten()
            AOD = gdal.Open(AOD_key).ReadAsArray().flatten()
                        
            AOD = AOD.astype('float')
            AOD[AOD == -28672] = n.nan
            print(len(AOD))
            AOD = AOD * 0.001 #scale factor provided by HDF view app
            conditions = (AOD>-9.9, lonmin<lon, lon<lonmax, latmin<lat, lat<latmax)
            indices = n.where(n.logical_and.reduce(conditions))
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
            outputfile=output_path+'/MAIAC_ACAL_{}_{}'.format(year,dayfname)+'.txt'
            
            resampled_AOD=[]
            for i in range(len(df)):
                #print(i)
                con = ((df.iloc[i,1]-.01)<MAIAC_temp['lon'].values, MAIAC_temp['lon'].values <(df.iloc[i,1]+.01), (df.iloc[i,2]-.01)<MAIAC_temp['lat'].values , MAIAC_temp['lat'].values <(df.iloc[i,2]+.01))
                ind= n.where(n.logical_and.reduce(con))
                #print(ind)
                if not n.any(ind):
                    resampled_AOD.append(-999.0) 
                    #print('------------ NULL')
                else:
                    resampled_AOD.append(MAIAC_temp['AOD'].values[ind].mean())
            df['AOD']=resampled_AOD  #pd.concat(df,resampled_AOD)
            newDF=df.loc[:,'POINT_X':'AOD']
            print ('Writing output ...')
            if len(MAIAC_temp['AOD'])>0:
              if os.path.exists(outputfile): # is the same day exists beacuse of multiple granuels form the same day
                EF=pd.read_csv(outputfile, sep=' ', header=None)
                
                # where both of the values are not NAN
                con = (newDF['AOD'] != -999.0, EF.iloc[:,-1] != -999.0 )
                ind = n.where(n.logical_and.reduce(con))
                newDF['AOD'].values[ind]=(newDF.iloc[:,-1].values[ind]+EF.iloc[:,-1].values[ind])/2
                #where AOD from the previous granuale was NAN
                con = (newDF['AOD'] == -999.0, EF.iloc[:,-1] != -999.0 )
                ind = n.where(n.logical_and.reduce(con))
                newDF['AOD'].values[ind]=EF.iloc[:,-1].values[ind]/2
                
                
                with open(outputfile, 'w') as of:
                    
                    
                    newDF.to_csv(of, header=None, index=None, sep=' ')
                of.close()
              else:
                newDF.to_csv(outputfile, header=None, index=None, sep=' ')
            else: #when the seelcted region have no data
                 if os.path.exists(outputfile):
                    print ('No need to write a nan file since already file with data exists')
                 else:
                    newDF.to_csv(outputfile, header=None, index=None, sep=' ')
                 
            #newDF.to_csv(r'/Volumes/F/CAARE_2017/CAARE_Barik/hindcasting/MAIAC_{}/MAIAC_ACAL_{}_{}'.format(year,year,dayfname)+'.txt', header=None, index=None, sep=' ')
            




print ('Done! Total time taken to run: ', time.time() - start)
