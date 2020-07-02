library(lubridate)
library(tidyr)
library(dplyr)
library(sf)

PM <- read_csv("GitHub/PM_prediction/Data/AQS/EPA_2017.csv")

PM$Date <- as.Date(PM$Date, "%m/%d/%Y")

PM$Day <- paste0("Day", yday(PM$Date))

names(PM)[c(3, 5, 19, 20, 21)] <- c("ID","PM", "Latitude", "Longitude", "Day")

PM <- filter(PM, Longitude > -123.5 & Longitude < -120.8 & Latitude > 36.8 & Latitude < 39)

PM <- pivot_wider(PM, id_cols = c("ID", "Latitude", "Longitude"), names_from = Day, values_from = PM, values_fn = mean)

#There were some doubles for some reason so I just took the average. 

PM <- st_as_sf(PM, coords = c("Longitude", "Latitude"), crs = 4326, agr = "constant")

st_write(PM, dsn = "GitHub/PM_prediction/Data/AQS/PM.shp")
