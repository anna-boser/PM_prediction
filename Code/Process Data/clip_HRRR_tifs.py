# -*- coding: utf-8 -*-
"""
Spyder Editor

playing with arc- clip a massive amount of tiffs
"""
import arcpy
import os


arcpy.env.workspace = "C:\\Users\\aboser\\Documents\\GitHub\\PM_prediction\\Data\\HRRR\\tiffs\\"

directory = r'C:\\Users\\aboser\\Documents\\GitHub\\PM_prediction\\Data\\HRRR\\tiffs\\' # name of the HRRR directory
output_directory = r'C:\\Users\\aboser\\Documents\\GitHub\\PM_prediction\\Data\\HRRR\\clipped_tiffs\\' # separate output directory
#print ('Running files inside {}'.format(directory))
file_names = os.listdir(directory)      #files within the filepath
ct = 0
for file in file_names:
    if file.endswith('.tif') == True:
        print('clipping file: ' + file)
        arcpy.Clip_management(file,  "-2556520.142522 -624306.152557 -1323520.142522 800693.847443",
                      output_directory + 'Clipped' + file, 'C:\\Users\\aboser\\Documents\\GitHub\\PM_prediction\\Data\\fishnet\\Modeling_Grid.shp',
                      '-9999', "ClippingGeometry", 'NO_MAINTAIN_EXTENT')
    ct+=1

