library(sf)
NEI <- st_read("~/GitHub/PM_prediction/Data/NEI/NEI_Shape/cropped_point_NEI.shp", layer = "cropped_point_NEI")
NEI$ann_value <- as.numeric(NEI$ann_value)
