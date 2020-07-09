#This script takes the plume df and the Modeling_Grid and creates a data frame with the cell IDs and the day and the presence of plumes by density

library(sf)
library(dplyr)


# HMS <- st_read("~/GitHub/PM_prediction/Data/HMS/Plumes.shp", layer = "Plumes") #for some reason no Density?
HMS <- readRDS("~/GitHub/PM_prediction/Data/HMS/Plumes.RData")
HMS <- st_transform(HMS, 4326)

grid <- st_read("~/GitHub/PM_prediction/Data/fishnet/Modeling_Grid.shp", layer = "Modeling_Grid")

date_list <- seq.Date(from = as.Date("2017-01-01"), to = as.Date("2017-12-31"), by = "day")

Low_df <- data.frame(Id = grid$Id, matrix(data = 0, nrow = nrow(grid), ncol = length(date_list)))
colnames(Low_df) <- c("Id", paste0("Day", 1:365))
Med_df <- Low_df #duplicate empty dataset
High_df <- Low_df

for (day in 1:365){
  date <- date_list[day]
  plumes <- filter(HMS, DATE == date)
  if (nrow(plumes) != 0){
    low_p <- filter(plumes, Density == "Low")
    if(nrow(low_p != 0)){
      int <- st_intersection(grid, low_p)
      Low_df[int$Id, day + 1] <- 1
    }
    med_p <- filter(plumes, Density == "Med")
    if(nrow(med_p != 0)){
      int <- st_intersection(grid, med_p)
      Med_df[int$Id, day + 1] <- 1
    }
    high_p <- filter(plumes, Density == "High")
    if(nrow(high_p != 0)){
      int <- st_intersection(grid, high_p)
      High_df[int$Id, day + 1] <- 1
    }
  }
}
  
write.csv(Low_df, "~/GitHub/PM_prediction/Data/Variables/Low_Plumes/Low_Plumes.csv")
write.csv(Med_df, "~/GitHub/PM_prediction/Data/Variables/Med_Plumes/Med_Plumes.csv")
write.csv(High_df, "~/GitHub/PM_prediction/Data/Variables/High_Plumes/High_Plumes.csv")
