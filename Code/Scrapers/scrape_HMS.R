# This script is to retrieve HMS data from the NOAA website. 

library(data.table)
library(sf)
library(dplyr)
library(lubridate)

date_list <- seq(ymd('2017-01-01'), ymd('2017-12-31'), by = '1 day')

for (i in 1:length(date_list)) {
  date <- date_list[i]
  year <- year(date)
  month <- month(date)
  if (month %in% c(1:9)){
    month <- paste0("0", month)
  }
  day <- day(date)
  if (day %in% c(1:9)){
    day <- paste0("0", day)
  }
  HMSday <- paste0(year, month, day)
  
  #some are gz and some are not so you have to try both
  
  gzFiles <- 
    list(
      paste0(
        "http://satepsanone.nesdis.noaa.gov/pub/volcano/FIRE/HMS_ARCHIVE/",
        year,
        "/GIS/SMOKE/hms_smoke",
        HMSday,
        ".dbf.gz"
      ),
      paste0(
        "http://satepsanone.nesdis.noaa.gov/pub/volcano/FIRE/HMS_ARCHIVE/",
        year,
        "/GIS/SMOKE/hms_smoke",
        HMSday,
        ".shp.gz"
      ),
      paste0(
        "http://satepsanone.nesdis.noaa.gov/pub/volcano/FIRE/HMS_ARCHIVE/",
        year,
        "/GIS/SMOKE/hms_smoke",
        HMSday,
        ".shx.gz"
      )
    )
  
  gzDBFpath <- unlist(gzFiles[1])
  gzSHPpath <- unlist(gzFiles[2])
  gzSHXpath <- unlist(gzFiles[3])
  
  Files <- 
    list(
      paste0(
        "http://satepsanone.nesdis.noaa.gov/pub/volcano/FIRE/HMS_ARCHIVE/",
        year,
        "/GIS/SMOKE/hms_smoke",
        HMSday,
        ".dbf"
      ),
      paste0(
        "http://satepsanone.nesdis.noaa.gov/pub/volcano/FIRE/HMS_ARCHIVE/",
        year,
        "/GIS/SMOKE/hms_smoke",
        HMSday,
        ".shp"
      ),
      paste0(
        "http://satepsanone.nesdis.noaa.gov/pub/volcano/FIRE/HMS_ARCHIVE/",
        year,
        "/GIS/SMOKE/hms_smoke",
        HMSday,
        ".shx"
      )
    )
  
  DBFpath <- unlist(Files[1])
  SHPpath <- unlist(Files[2])
  SHXpath <- unlist(Files[3])
  
  dir <- "~/GitHub/PM_prediction/Data/HMS/Raw/"
  
  tryCatch({
    download.file(url = DBFpath, destfile = paste0(dir, "hms_smoke", HMSday, ".dbf"))
    download.file(url = SHPpath, destfile = paste0(dir, "hms_smoke", HMSday, ".shp"))
    download.file(url = SHXpath, destfile = paste0(dir, "hms_smoke", HMSday, ".shx"))
  }, error=function(e){})
  
  tryCatch({
    download.file(url = gzDBFpath, destfile = paste0(dir, "hms_smoke", HMSday, ".dbf.gz"))
    download.file(url = gzSHPpath, destfile = paste0(dir, "hms_smoke", HMSday, ".shp.gz"))
    download.file(url = gzSHXpath, destfile = paste0(dir, "hms_smoke", HMSday, ".shx.gz"))
  }, error=function(e){})
  
  print(i)
  
}


# to unzip all the gz files use terminal command gunzip *.gz