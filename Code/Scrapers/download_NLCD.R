#Download 2016 NLCD data

dir <- "~/GitHub/PM_prediction/Data/NLCD/"

download.file(url = 'https://s3-us-west-2.amazonaws.com/mrlc/NLCD_2016_Land_Cover_L48_20190424.zip', destfile = paste0(dir, "NLCD_2016.zip"))