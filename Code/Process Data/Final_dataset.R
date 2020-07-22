library(sf)
library(tidyr)
library(dplyr)

memory.limit(size=100000)

centroids <- read.csv("C:\\Users\\aboser\\Documents\\GitHub\\PM_prediction\\Data\\fishnet\\fishnet_centroids_LatLon.csv", header = TRUE)

elevation <- st_read("C:\\Users\\aboser\\Documents\\GitHub\\PM_prediction\\Data\\Variables\\Elevation\\Elevation.shp", "Elevation")
emissions <- st_read("C:\\Users\\aboser\\Documents\\GitHub\\PM_prediction\\Data\\Variables\\Emissions\\Emissions.shp", "Emissions")
land_cover <- read.table("C:\\Users\\aboser\\Documents\\GitHub\\PM_prediction\\Data\\Variables\\Land_Cover\\Land_Cover.txt", header = TRUE, sep = ",")
roads <-  st_read("C:\\Users\\aboser\\Documents\\GitHub\\PM_prediction\\Data\\Variables\\Roads\\Roads.shp", "Roads")
streets <-  st_read("C:\\Users\\aboser\\Documents\\GitHub\\PM_prediction\\Data\\Variables\\Streets\\Streets.shp", "Streets")

constants <- data.frame("Id" = elevation$Id, 
                        "Day" = NA,
                        "Unique" = NA,
                        "Lat" = centroids$Y, 
                        "Lon" = centroids$X,
                        "Elevation" = elevation$MEAN, 
                        "Emissions" = emissions$Sum_ann_va, 
                        "Forest" = land_cover$FOREST, 
                        "Roads" = roads$Sum_Shape_, 
                        "Streets" = streets$Sum_Shape_)

rm(elevation)
rm(emissions)
rm(land_cover)
rm(roads)
rm(streets)
rm(centroids)

dates <- 1:365
Daily_df <- constants[rep(seq_len(nrow(constants)), each = length(dates)),]
Daily_df$Day <- rep(dates, nrow(constants))
Daily_df$Unique <- paste0(Daily_df$Id, "_", Daily_df$Day)

rm(constants)
rm(dates)

high_plumes <- read.csv("C:\\Users\\aboser\\Documents\\GitHub\\PM_prediction\\Data\\Variables\\High_Plumes\\High_Plumes.csv")
med_plumes <- read.csv("C:\\Users\\aboser\\Documents\\GitHub\\PM_prediction\\Data\\Variables\\Med_Plumes\\Med_Plumes.csv")
low_plumes <- read.csv("C:\\Users\\aboser\\Documents\\GitHub\\PM_prediction\\Data\\Variables\\Low_Plumes\\Low_Plumes.csv")

Daily_df$Plumes_High <- pivot_longer(high_plumes, 3:367, names_to = "Day")$value
Daily_df$Plumes_Med <- pivot_longer(med_plumes, 3:367, names_to = "Day")$value
Daily_df$Plumes_Low <- pivot_longer(low_plumes, 3:367, names_to = "Day")$value

rm(high_plumes)
rm(med_plumes)
rm(low_plumes)

max_temp <- st_read("C:\\Users\\aboser\\Documents\\GitHub\\PM_prediction\\Data\\Variables\\Max_Temp\\Max_Temp.shp", "Max_Temp") 
max_wind <- st_read("C:\\Users\\aboser\\Documents\\GitHub\\PM_prediction\\Data\\Variables\\Max_wind\\Wind_speed.shp", "Wind_speed")
precipitation <- st_read("C:\\Users\\aboser\\Documents\\GitHub\\PM_prediction\\Data\\Variables\\Precipitation\\Precipitation.shp", "Precipitation")
relative_humidity <- st_read("C:\\Users\\aboser\\Documents\\GitHub\\PM_prediction\\Data\\Variables\\Relative_Humidity\\Relative_Humidity.shp", "Relative_Humidity")
wind_direction <- st_read("C:\\Users\\aboser\\Documents\\GitHub\\PM_prediction\\Data\\Variables\\Wind_direction\\Wind_direction.shp", "Wind_direction")

max_temp$geometry <- NULL
max_wind$geometry <- NULL
precipitation$geometry <- NULL
relative_humidity$geometry <- NULL
wind_direction$geometry <- NULL

Daily_df$Max_Temp <- pivot_longer(max_temp, 9:373, names_to = "Day")$value
rm(max_temp)

Daily_df$Max_Wind <- pivot_longer(max_wind, 9:373, names_to = "Day")$value
rm(max_wind)

Daily_df$Precip <- pivot_longer(precipitation, 9:373, names_to = "Day")$value
rm(precipitation)

Daily_df$Rel_Humidity <- pivot_longer(relative_humidity, 9:373, names_to = "Day")$value
rm(relative_humidity)

wind_direction <- pivot_longer(wind_direction, 9:373, names_to = "Day", values_to = "Wind_Dir")
wind_direction$Unique <- paste0(wind_direction$Id, "_", substr(wind_direction$Day, 8, 10))
wind_direction <- select(wind_direction, c("Unique", "Wind_Dir"))
Daily_df <- merge(x = Daily_df, y = wind_direction, by = "Unique", all.x = TRUE)
# Daily_df$Wind_Dir <- pivot_longer(wind_direction, 9:373, names_to = "Day")$value #not sure why this is not matching up quite right
rm(wind_direction)

Daily_df$Max_Temp[Daily_df$Max_Temp < -30] <- NA #this gets rid of the -999 values and those that were averaged to something closer to -400 due to neighboring values
Daily_df$Max_Wind[Daily_df$Max_Wind < 0] <- NA
Daily_df$Precip[Daily_df$Precip < 0] <- NA
Daily_df$Rel_Humidity[Daily_df$Rel_Humidity < 0] <- NA
Daily_df$Wind_Dir[Daily_df$Wind_Dir < 0] <- NA

#add a time lagged precipitation because precipitation probably affects PM2.5 like two days after
precip_lag <- function(row, lag){
  location <- as.integer(row["Id"])
  day <- as.integer(row["Day"])
  fil <- filter(Data, Id == location, Day == day - lag)
  if (nrow(fil) == 0){
    val = NA
  } else {
    val = fil$Precip
  }
  val
}

# Daily_df$Precip_lag_1 <- apply(Data, 1, precip_lag, lag = 1) # I looked at these and they're even more useless for predicting PM than just Precipitation. 
# Daily_df$Precip_lag_2 <- apply(Data, 1, precip_lag, lag = 2)

boundary_layer <- read.table("C:\\Users\\aboser\\Documents\\GitHub\\PM_prediction\\Data\\Variables\\Boundary_Layer\\B_layer.txt", header = TRUE, sep = ",")
boundary_layer <- pivot_longer(boundary_layer, 5:363, names_to = "Day", values_to = "BLH")
boundary_layer$Date <- as.Date(substr(boundary_layer$Day, 8, 15), format = "%Y%m%d")
boundary_layer$Day <- as.integer(strftime(boundary_layer$Date, format = "%j"))
boundary_layer$Unique <- paste0(boundary_layer$FISHNET_LABELS, "_", boundary_layer$Day)
boundary_layer <- select(boundary_layer, c("Unique", "BLH"))

Daily_df <- merge(x = Daily_df, y = boundary_layer, by = "Unique", all.x = TRUE)
rm(boundary_layer)

All_AOD <- list.files(path = "C:\\Users\\aboser\\Documents\\GitHub\\PM_prediction\\Data\\Variables\\AOD\\", pattern = "MAIAC")
Read_AOD <- function(filename){
  tmp <- read.table(paste0("C:\\Users\\aboser\\Documents\\GitHub\\PM_prediction\\Data\\Variables\\AOD\\", filename), header = FALSE, sep = " ")
  tmp <- data.frame("Id" = tmp$V4, "AOD" = tmp$V5)
  tmp$Day <- as.integer(substr(filename, 17, 19))
  tmp$Unique <- paste0(tmp$Id, "_", tmp$Day)
  tmp <- select(tmp, c("Unique", "AOD"))
  tmp
}
AOD_List <- lapply(All_AOD, Read_AOD)
aod <- Reduce(rbind, AOD_List)

rm(All_AOD)
rm(Read_AOD)
rm(AOD_List)

Daily_df <- merge(x = Daily_df, y = aod, by = "Unique", all.x = TRUE)
rm(aod)

Daily_df$AOD[Daily_df$AOD == -999] <- NA

pm <- st_read("C:\\Users\\aboser\\Documents\\GitHub\\PM_prediction\\Data\\Variables\\PM\\PM.shp", "PM")
pm$geometry <- NULL

pm <- pivot_longer(pm, 4:368, names_to = "Day", values_to = "PM")
pm$Day <- substr(pm$Day, 8, 10)
pm$Unique <- paste0(pm$Id, "_", pm$Day)
pm <- select(pm, c("Unique", "PM"))

Daily_df <- merge(x = Daily_df, y = pm, by = "Unique", all.x = TRUE)
rm(pm)

Daily_df$PM[Daily_df$PM <= 0] <- NA

write.csv(Daily_df, file = "C:\\Users\\aboser\\Documents\\GitHub\\PM_prediction\\Data\\Final_DFs\\Full.csv", row.names = FALSE)

filter(Daily_df, Day <= 333) %>% write.csv(file = "C:\\Users\\aboser\\Documents\\GitHub\\PM_prediction\\Data\\Final_DFs\\With_AOD.csv", row.names = FALSE)

filter(Daily_df, Day <= 333 & !is.na(PM)) %>% write.csv(file = "C:\\Users\\aboser\\Documents\\GitHub\\PM_prediction\\Data\\Final_DFs\\Train.csv", row.names = FALSE)
