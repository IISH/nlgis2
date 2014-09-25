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
view.nlg(1975, "testmap")

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
  browseURL(topomap)      
}
view.nlt(1812, "nld_topo_1812")


