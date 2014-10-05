# File: nlgis_leaflet01.R
# Date: 20140923
# Purpose: function to download and view nlgis maps locally
# Last change: 
## version 2: new dev version allows for topojson as well. checking it out.


require(leafletR)

view.nlg <- function(year, name){
  ply <- download.file(url = paste0(paste0("http://node-128.dev.socialhistoryservices.org/api/maps?year=",
                                           year), "&format=geojson"),
                       destfile = paste0(name, ".geojson"))
  geomap <- leaflet(paste0("./", paste0(name, ".geojson")),
                    title = paste0("Netherlands - ", year))
  browseURL(geomap)      
}
# to run script use something like:
# view.nlg(year = 1842, name = "its_working")
view.nlg(1812, "testmap")

## installing new dev version of leafletR
if(!require(devtools)) install.packages("devtools")
devtools::install_github("leafletR", "chgrl", "topo")
library(leafletR)

view.nlt <- function(year, name){
  ply <- download.file(url = paste0("http://node-128.dev.socialhistoryservices.org/api/maps?year=",
                                           year),
                       destfile = paste0(name, ".json"))
  topomap <- leaflet(paste0("./", paste0(name, ".json")),
                    title = paste0("Netherlands - ", year))
  #browseURL(topomap)      
}
testmapview.nlt(1812, "nld_topo_1812")

library(jsonlite)
testdata <- as.data.frame(
  fromJSON("http://node-128.dev.socialhistoryservices.org/api/data?year=1977"))

test.dat <- toGeoJSON(data=testdata[1:100,], dest=tempdir(), name="test_data")




testmap <- view.nlt(1812, "nld_topo_1812")


#
library(leafletR)
library(jsonlite)
download.file("http://node-128.dev.socialhistoryservices.org/api/maps?year=1937",
                     destfile = paste0("testmap", ".json"))
map <- leaflet("./testmap.json")
map # displays map in browser


test <- readOGR(dsn = "./testmap.json", driver="GeoJSON")

testdata <- 
  fromJSON("http://node-128.dev.socialhistoryservices.org/api/data?code=TXCU")

table(testdata$data$year)

map.shape <- spTransform(map)

#####
require(rgdal) 
any(grepl("GeoJSON", ogrDrivers()$name)) ### TRUE 
url <- " 
https://raw.github.com/johan/world.geo.json/master/countries.geo.json" 
world <- readOGR(dsn = url, layer = "OGRGeoJSON") 
plot(world) 

### attempt to use data and geojson api to plot results
library(leafletR)
library(jsonlite)
library(rgdal)
library(sp)


# get data
testdata <- 
  fromJSON("http://node-128.dev.socialhistoryservices.org/api/data?year=1977")

# get map (and showmap using leaflet)
download.file(
  "http://node-128.dev.socialhistoryservices.org/api/maps?year=1977&format=geojson",
              destfile = paste0("testmap2", ".geojson"))

# mapdata <- fromJSON(
#   "http://node-128.dev.socialhistoryservices.org/api/maps?year=1977&format=geojson"
#   )

map = readOGR("testmap2.geojson", "OGRGeoJSON")
plot(map)

#subsetting testdata (due to different 'codes'
# unsure of meaning, just selecting a single one)
testdata.sub <- subset(testdata$data, code == "TEPV", 
                       select = c("amsterdam_code",
                                  "value"))
table(duplicated(testdata.sub$amsterdam_code))
testdata.sub1 <- subset(testdata.sub, !duplicated(amsterdam_code))
                        
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


writeOGR(map, "./mapTK2.geojson", layer = "value", driver='GeoJSON') 
writeOGR(map, "./mapTK3.geojson", layer = c("value", "naam"), driver='GeoJSON') 
# NB error upon overwrite

cuts = c(7,500,1000,3194, 2488, 10000, 10000)
sty<-styleGrad(prop="value", breaks=cuts, right=FALSE, style.par="col",
               style.val=rev(heat.colors(6)), leg="value TK 1977", lwd=1)
popup<-c("name", "value")
lfmap <- leaflet("./mapTK.geojson", incl.data = TRUE, popup=popup, style = sty)

lfmap # displays map in browser

