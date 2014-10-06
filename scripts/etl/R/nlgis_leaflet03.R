# File: nlgis_leaflet03.R
# Date: Oct 5, 2014
# Author: richard.zijdeman@iisg.nl
# Last change: none so far

# clean workspace
rm(list=ls())

### attempt to use data and geojson api to plot results
library(leafletR)
library(jsonlite)
library(rgdal)
library(sp)


# get data ####
testdata <- 
  fromJSON("http://node-128.dev.socialhistoryservices.org/api/data?year=1977")

# get map (and showmap using leaflet) ####
download.file(
  "http://node-128.dev.socialhistoryservices.org/api/maps?year=1977&format=geojson",
  destfile = paste0("testmap2", ".geojson"))

# mapdata <- fromJSON(
#   "http://node-128.dev.socialhistoryservices.org/api/maps?year=1977&format=geojson"
#   )

map = readOGR("testmap2.geojson", "OGRGeoJSON")
plot(map)

# subsetting testdata (due to different 'codes' ####
# unsure of meaning, just selecting a single one)
testdata.sub <- subset(testdata$data, code == "TEPV", 
                       select = c("amsterdam_code",
                                  "value"))
table(duplicated(testdata.sub$amsterdam_code))
testdata.sub1 <- subset(testdata.sub, !duplicated(amsterdam_code))

# plot data the traditional way: ####
map@data <- merge(map@data, testdata.sub1,
                  by.x = "amsterdamcode",
                  by.y = "amsterdam_code",
                  all.x = TRUE)

at = c(7,500,1000,3194, 2488, 10000, 10000)
col = rev(heat.colors(length(at)))


mapvalues <- spplot(map,"value", at = at, col.regions = col, 
                    cuts = length(at),
                    main=list(label="value of TK", cex=2))
mapvalues # works!

# plot data using leafletR ####
writeOGR(map, "./mapTK3.geojson", layer = c("value", "naam"), driver='GeoJSON') 
# NB error upon overwrite

cuts = c(7,500,1000,3194, 2488, 10000, 10000)
sty<-styleGrad(prop="value", breaks=cuts, right=FALSE, style.par="col",
               style.val=rev(heat.colors(6)), leg="value TK 1977", lwd=1)
popup<-c("name", "value")
lfmap <- leaflet("./mapTK.geojson", incl.data = TRUE, popup=popup, style = sty)

lfmap # displays map in browser
# click on area for popup