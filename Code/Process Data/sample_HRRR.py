# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 12:29:30 2020

@author: lcohen2
"""

# Description: Creates a table that shows the values of cells from 
#              a raster, or set of rasters, for defined locations. 
#              The locations are defined by raster cells or by a set 
#              of points.
# Requirements: Spatial Analyst Extension

# Import system modules
import arcpy
from arcpy import env
from arcpy.sa import Sample
import os

# Set environment settings
env.workspace = "C:\\Users\\aboser\\Documents\\GitHub\\PM_prediction\\Data\\HRRR\\clipped_tiffs\\"

directory = r'C:\\Users\\aboser\\Documents\\GitHub\\PM_prediction\\Data\\HRRR\\clipped_tiffs\\' # name of the HRRR directory
#out_directory = r'C:\Users\lcohen2\Desktop\Data\Big_Table\\' # separate output directory for table

locations = 'C:\\Users\\aboser\\Documents\\GitHub\\PM_prediction\\Data\\fishnet\\Modeling_Grid.shp'
outTable = "C:\\Users\\aboser\\Documents\\GitHub\\PM_prediction\\Data\\Variables\\Boundary_Layer\\Big_Table.dbf"
sampMethod = "NEAREST"
unique_value = "Id"

file_names = os.listdir(directory)
# Set local variables
inRasters = []
for file in file_names:
    if (file.endswith('.tif') == True) and ('experiment' not in file):
        inRasters.append(file)
        # print(file)

# # Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

# # Execute Sample
Sample(inRasters, locations, outTable, sampMethod, unique_id_field=unique_value)

