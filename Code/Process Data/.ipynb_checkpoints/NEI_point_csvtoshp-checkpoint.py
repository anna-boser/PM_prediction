import numpy as np
import pandas as pd
import geopandas as gpd

my_data = pd.read_csv('C:\\Uscondaers\\phili\\Documents\\Anna-Project\\PM_prediction\\Data\\NEI\\cropped_point_NEI.csv', low_memory=False)
my_data = np.array(my_data)
my_data = np.delete(my_data, 0, 1)
print(my_data)