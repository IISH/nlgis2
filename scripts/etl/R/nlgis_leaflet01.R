# File: nlgis_leaflet01.R
# Date: 20140923
# Purpose: function to download and view nlgis maps locally
# Last change: None so far


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