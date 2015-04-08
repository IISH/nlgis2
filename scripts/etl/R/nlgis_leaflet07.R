# File: nlgis_leaflet05.R
# Date: Oct 6, 2014
# Author: richard.zijdeman@iisg.nl
# Last change: none so far

# clean workspace
rm(list=ls())

### attempt to use data and geojson api to plot results
library(leafletR)
library(jsonlite)
library(rgdal)
library(sp)

# get data
somedata <- 
  fromJSON("http://node-128.dev.socialhistoryservices.org/api/data?year=1937")


# oct 18, 2014: it appears the structure of the data api has changed...
somedata <- 
  fromJSON("http://node-128.dev.socialhistoryservices.org/api/data?code=TXCU")



# select relevant subset
somedata.1 <- subset(somedata$data, code == "TXCU", 
                        select = c("amsterdam_code", "naam", "year", 
                                   "value"))
table(somedata.1$year)

somedata.1 <- subset(somedata$code == "VES3", 
                     select = c("amsterdam_code","naam", 
                                "value"))


somedata.2 <- subset(somedata.1, !duplicated(amsterdam_code))

# NB: amsterdam_code is type character, while it is 'int' in map@data
somedata.2$amsterdam_code <- as.integer(somedata.2$amsterdam_code)

# get map
download.file(
  "http://node-128.dev.socialhistoryservices.org/api/maps?year=1937&format=geojson",
  destfile = paste0("map1937", ".geojson"))

map <- readOGR("map1937.geojson", "OGRGeoJSON")

# to merge with data.frame from SpatialPolygonsDataFrame it is advised to 
# take out data.frame, do the merge and put it back in.  
temp <- map@data
temp$sorder <- c(1:length(temp$id))

temp2 <- merge(temp, somedata.2,
               by.x = "amsterdamcode",
               by.y = "amsterdam_code",
               all.x = TRUE, sort = FALSE)
temp3 <- temp2[order(temp2$sorder), ]

# overwrite map@data with merged data.frame
map@data <- temp3
writeOGR(map, "./mapTK1937_4.geojson", layer = "", 
         driver='GeoJSON') 

# plot the data
cuts = seq(round(min(map@data$value, na.rm = TRUE),0), 
           round(max(map@data$value, na.rm = TRUE),0), 
           length=8)
sty<-styleGrad(prop="value", breaks=cuts, right=FALSE, style.par="col",
               style.val=rev(heat.colors(8)), 
                leg="RK Staatspartij votes,Tweede Kamer, 1937", lwd=1)
popup<-c("name", "amsterdamcode", "value") 

# create map
lfmap <- leaflet("./mapTK1937_4.geojson", incl.data = TRUE, popup=popup, 
                 style = sty, base.map = "mqsat")
lfmap # 

# trying to add base_map
addBaseMap(
  name="nl1800", 
  title="nl1800", 
  url="http://maps.nypl.org/warper/maps/tile/7398/{z}/{x}/{y}.png",
  options=list(
    attribution='&copy; <a href="http://maps.nypl.org/warper/", target=
      "_blank">NYPL Map Warper</a>'
  )
)

lfmap <- leaflet("./mapTK1937_4.geojson", incl.data = TRUE, popup=popup, 
                 style = sty, base.map = c("mqsat","nl1800"))
lfmap # 
