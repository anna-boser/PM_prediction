# PM_prediction
Repository for my NASA CAARE Internship project 2020. 

## Goal
The goal of this project is to create an accurate and high resolution (1km2) dataset of PM2.5 estimates that covers the San Francisco Bay Area by training and comparing comprehensive machine learning and statistical models using pertinent parameters. 

### Abstract: 
Ambient fine particulate matter (PM2.5) is associated with significant adverse health impacts. Continuous, high quality and high resolution PM2.5 data has the potential to be greatly useful in public health research and mitigation efforts, but PM2.5 monitors are few and unevenly distributed over the landscape. In California, this is of particular concern because catastrophic wildfires have caused and are projected to continue causing episodes of very high levels of PM2.5. Previous studies have shown the potential for Aerosol Optical Depth (AOD), meteorological data, and land cover/land use (LCLU) data to estimate PM2.5 using a variety of models. However, the most recent research has yet to be applied in the San Francisco Bay Area, where high density episodes of PM2.5 were observed in 2017 and 2018. In addition, few studies have taken advantage of flexible and powerful machine learning algorithms to estimate PM2.5 levels, especially considering the variety of parameters known to improve such models. This study aims to apply the state of the art PM2.5 estimation techniques, including a proven two-stage model trained on AOD, meteorological, and LCLU data, and compare it to promising ML algorithms including random forests and gradient boosted decision trees. We envision that this approach will lead to greatly improved estimation of PM2.5 in California, and that more flexible ML techniques will allow for improved results when predicting extreme PM2.5 events, such as resulting from a wildfire, which are particularly important for public health research. 

More information on the motivations and methods can be referenced in the **Poster_Presentation** folder. More information on the data used can be found below. 

### Description of data used: 
* *AQS*: Data from the Environmental Protection Agency's (EPA) Air Quality System (AQS). This is a network of federal, highly acurate ground level air quality sensors which provide daily information on PM2.5. The 34 monitors located within our training site are used train our models. 
#### Parameters:
* *HMS*: The National Oceanic and Atmospheric Administration's (NOAA) Hazard Mapping System (HMS) includes a daily plume product which constitutes remotely sensed smoke plumes from wildfires categroized by three different levels of density. 
* *MAIAC*: This is daily data at a 1km^2^ resolution of Aerosol Optical Depth (AOD) calculated from data from NASA's Terra and Aqua satellites. 
* *NED*: The US Geological Survey's (USGS) National Elevation Dataset (NED)
* *NEI*: The EPA's National Emissions Inventory (NEI). We used point emissions of PM2.5. 
* *NLCD*: The National Land Cover Database (NLCD) provides us with an assessment land cover type. We kept whether or not a pixel was a forest as an explanatory variable. 
* *NLDAS*: The North American Land Data Assimilation System's (NLDAS) meteorological data provided us with maximum temperature, precipitation, wind speed, wind direction, and relative humidity at a 30 km^2^ resolution. 
* *TIGER*: Topologically Integrated Geographic Encoding and Referencing (TIGER) gives us a line shapefile of roads and streets. 

## Steps and files needed: 

The **Code** folder holds the code used to **Scrape** the data, process it (**Process Data**), and train models (**Modeling**). 
The **Data** folder holds all of the raw and processed data used to train models and create figures (in **Final_DFs**). 

### 1) Scrape data and resample data to 1km^2^ grid
* **Run the scrapers to assemble the needed data.** Some scrapers are missing -- sorry. Feel free to contact me about that. 
* **Use ArcGIS to create two polygon fishnets, or grids that are at a 1km^2^ resolution.** One is for training only, the other, smaller one, is for creating maps. To do this: 

*Large*: (for training)

Top: 39
Right: 120.8 W
Bottom: 36.8
Left: 123.5 W

Number of rows: 244
Number of columns: 236

*Small*: (actual target area: for testing) 

Create a fishnet with these dimensions and only 1 column and row:
-122.8, 37.2, -121.7, 38.3
Then clip the large one and only keep the cells within the smaller fishnet. 

These fishnets are stored under **Data/fishnet**. The large one is **Modeling_Grid** and the small one is **small_grid**. 


* **Then do zonal statistics in order to resample all variables to the grid:**

*Land_Cover*: 
* Created using the clipped NLCD 2016 data
* Calculated Majority as statistic. Rowid is the cell id. 
* Created a “FOREST” attribute using the folloing code: 

Dim FOREST
If [MAJORITY] = 41 Then
FOREST = 1


elseif [MAJORITY] = 42 Then
FOREST = 1


elseif [MAJORITY] = 43 Then
FOREST = 1


else
FOREST = 0
end if

* Saved as land_cover

*Max_Temp*:
* Used Clipped_Max_Temp_NLDAS
* Calculated Average value using a spatial join
* Saved as a shapefile called Max_Temp
* Id is the Cell_ID
* Max_wind, Wind_Direction, Precipitation, Relative humidity all use the same process as above. 

*Roads*: 
* Used TIGER primary and secondary roads
* Did an intersection with output as “Line”
* Did a spatial join with target Modeling_Grid and sum to get road lengths in each cell
* Length of road output is Sum_Shape
* Id is the Cell_ID. 

*Streets*: 
* Used TIGER streets
* Did an intersection with output as “Line”
* Did a spatial join with target Modeling_Grid and sum to get road lengths in each cell
* Length of road output is Sum_Shape
* Id is the Cell_ID. 

*PM*:
* From the Nasa AQS daily averages
* Reformatted according to the AQS_processing script
* Did a spatial join and got average values
* Shapefile saved as PM

*Emissions*:
* Used NEI point emissions data only. Filtered lat/lon and selected only PM2.5 (PM25-Pri, PMfine, PM25-Fil, PM-Con) and put in a shapefile. (WGS 1984)
* Had to add a quick step making the ann_value numeric -- r script
* Spatial join sum to get the sum of all the emissions in each point. 

*Elevation*:
* National elevation data. Mosaiced and then calculated the average statistic. 

*Boundary layer*:
* Converted to tiff and resampled using fishnet_label.shp in ArcGIS. 

*AOD*:
* From https://portal.nccs.nasa.gov/datashare/maiac/DataRelease/NorthAmerica_2000-2016/h01v04/2017/
* In terminal: wget -A hdf -m -p -E -K -K -np https://portal.nccs.nasa.gov/datashare/maiac/DataRelease/NorthAmerica_2000-2016/h01v04/2017/
* Used **MAIAC_AOD_Data_Processing.ipynb**. 


### 2) Merge into the final grid and create the training dataset

Use **Final_dataset.R**. All variables were fused together into **Full_df**. Then the days missing AOD at the end of 2017 were removed to make **w_AOD** and then I filtered the data to have a dataset that only has the training data (PM monitor locations) which I called **Train**. 

### 3) Train and evaluate the statistical model 

Use **Two_stage.Rmd**. 

### 4) Train and evaluate the ML models

Use **autogluon_try.ipynb**. 


