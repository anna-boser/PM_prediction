library(sf)
library(dplyr)

centroids <- st_read("~/GitHub/PM_prediction/Data/fishnet/fishnet_label.shp", layer = "fishnet_label")
coords <- st_coordinates(centroids) %>% as.data.frame()
coords$Id <- centroids$Id

write.csv(coords, "~/GitHub/PM_prediction/Data/fishnet/fishnet_centroids_LatLon.csv")
