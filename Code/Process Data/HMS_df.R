# This file creates a dataset with all the NOAA HMS plumes I will be using and add a PlumeID. It also changes the Density Variable to indicate "Low", "Medium", or "High". I filter my sample based on the following criteria: is within or has some part within California. Resulting dataframe(s): 
# "Plumes" with variables: DATE, Start, End, Density, geometry, PlumeID
# Number of Plumes: 20388

library(data.table)
library(sf)
library(tmap)
library(dplyr)
library(ggplot2)
library(lubridate)
library(raster)
library(sp)
library(tidyr)
library(grid)
library(latex2exp)
readin.proj=4269 #Jude said this one works well with the lat/lons provided for the plumes
DataDir <- "~/Documents/GitHub/PM_prediction/"

#Import layers California State Border
CA_State <- st_read(dsn = "~/Downloads/tl_2017_us_state", layer = "tl_2017_us_state") %>% 
  filter(NAME == "California") %>% 
  st_transform(crs=readin.proj) #same proj as plumes

#Make a list of all layer names
AllPlumes <- list.files(path = file.path(DataDir, "Data/HMS/"),
                        pattern = ".shp") %>% substr(1,17)

#Read every layer based on its name, add a date column and set crs
ReadPlumes <- function(PlumeName){
  tmp <- st_read(dsn = file.path(DataDir, "Data/HMS/"), layer = PlumeName)
  st_crs(tmp) <- readin.proj
  
  #Get rid of corrupt/invalid geometries
  tmp <- tmp %>% mutate(check=st_is_valid(.)) %>% filter(check == TRUE) %>% select(-check) #what days?? See below. 
  
  #Get all the plumes only within or partially within California
  withinPlumes <- st_join(tmp, 
                          CA_State, 
                          join = st_within)
  withinPlumes <- withinPlumes %>% filter(STATEFP == "06") 
  
  overlapsPlumes <- st_join(tmp, 
                            CA_State, 
                            join = st_overlaps)
  overlapsPlumes <- overlapsPlumes %>% filter(STATEFP == "06") 
  
  tmp <- rbind(withinPlumes, overlapsPlumes) %>% select(colnames(tmp))
  
  #Add Density if necessary
  if (!("Density" %in% colnames(tmp))) {
    tmp <- tmp %>% mutate(Density = rep(NA, nrow(tmp)))
  }
  
  #add date
  tmp <- tmp %>% 
    mutate(DATE = as.Date(substr(PlumeName, 10, 17), "%Y%m%d")) %>% 
    select(DATE, Start, End, Density, geometry) %>% 
    st_set_crs(readin.proj)
}

PlumeList <- lapply(AllPlumes, ReadPlumes)

#Bind all layers together into a single DF -- this takes forever don't run unless necessary
Plumes <- Reduce(rbind, PlumeList)

#Add unique IDs to each plume: 
Plumes <- mutate(Plumes, PlumeID = seq(1:nrow(Plumes)))



#make dates into dates
Plumes$DATE <- ymd(Plumes$DATE) #shouldn't this have already happened...



#Plumes <- filter(Plumes, !is.na(Density))

#Also for simplicity, I will replace Density with a categorical variable: Low, Med, and High. 
LMH <- function(value){
  if (is.na(value)) {
    NA
  } else {
    if (value == 5 | value == "5" | value == "5.000"){
      "Low"
    } else if (value == 16 | value == "16" | value == "16.000"){
      "Med"
    } else if (value == 27 | value == "27"| value == "27.000"){
      "High"
    }
  }
}
Plumes$Density <- lapply(Plumes$Density, LMH)


#Export unified DF
st_write(Plumes, dsn = file.path(DataDir, "Data/HMS/Plumes.shp", layer = "Plumes"))


#Visualizations/diagnostics

#Check which days are missing 
AllPlumes <- AllPlumes %>% substr(10,17)
AllPlumes <- AllPlumes %>% ymd()
alldates <- seq(min(AllPlumes), max(AllPlumes), by = 1)
missingdates <- alldates[!(alldates %in% AllPlumes)] #There are only a handful of missing dates so I'm not gonna worry about this


#Visualize when density starts happening
ggplot(Plumes) + geom_histogram(aes(x = DATE, fill = is.na(Density)), bins = 1000)
#We're kinda fucked lol. There only starts to be densities consistently starting in 2010. I'll do the analysis on the Plumes without densities too then. 

# In reality what I did: 
load("~/PM_exposure03:29:2020.RData")
Plumes <- filter(Plumes, year(DATE) == 2017)
DataDir <- "~/Documents/GitHub/PM_prediction/"
st_write(Plumes, dsn = file.path(DataDir, "Data/HMS/Plumes.shp"), layer = "Plumes") #for some reason this doesn't keep denisty
saveRDS(Plumes, file = file.path(DataDir, "Data/HMS/Plumes.RData"))

