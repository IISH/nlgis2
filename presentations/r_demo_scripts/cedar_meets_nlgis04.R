# File: cedar_meets_nlgis04.R
# Author: richard.zijdeman@iisg.nl
# Date: October 10, 2014
# Purpose: see whether you can retrieve data from CEDAR's SPARQLE endpoint and
#          plot them on map retrieved from NLGIS-2 API.
# Note: DATA SHOULD NOT BE INTERPRETED SUBSTANTIVELY (for debugging purposes only)
# Laste change: 
### 2015-03-20: version 04: new sparql endpoint based on mini-projects
### 2015-01-22: new trial-and-error of sparql queries
### 2014-10-19: Restricted query to specific call

# clean workspace
rm(list=ls())
dev.off()

# set working directory
setwd("/Users/RichardZ/tmp")

# load packages
library(SPARQL)
library(data.table)
library(stringr)
library(leafletR)
library(rgeos)
library(rgdal)

# prepare RDF data query
# endpoint <- "http://lod.cedar-project.nl/cedar/sparql"
endpoint <- "http://lod.cedar-project.nl/cedar-mini/sparql"

## Number of inhabited homes by muni in 1879 (thanks to Ashkan for the query)

sparql_prefix <- "PREFIX qb: <http://purl.org/linked-data/cube#>
  PREFIX cedar: <http://bit.ly/cedar#>
  PREFIX sdmx-dimension: <http://purl.org/linked-data/sdmx/2009/dimension#>
  PREFIX sdmx-code: <http://purl.org/linked-data/sdmx/2009/code#>"

query <- paste(sparql_prefix, "SELECT ?municipality ?year (SUM(?pop) AS ?tot)
      FROM <urn:graph:cedar-mini:release>
      WHERE { ?obs a qb:Observation . 
       ?obs cedar:population ?pop . 
       ?obs sdmx-dimension:refArea ?municipality .
       ?obs cedar:houseType <http://bit.ly/cedar#house-BewoondeHuizen> .        
       ?slice a qb:Slice.
       ?slice qb:observation ?obs.
       ?slice sdmx-dimension:refPeriod ?year .
       FILTER (NOT EXISTS {?obs cedar:isTotal ?total }) .
       FILTER (?year IN (1879)) .
} GROUP BY ?municipality ?year ORDER BY ?municipality")

res <- SPARQL(endpoint,query)$results
res$amsterdam_code <- substr(res$municipality, 
                             nchar(res$municipality)-5,
                             nchar(res$municipality)-1)

# get map from NLGIS-2 project
download.file(
  "http://nlgis.nl/api/maps?year=1879&format=geojson",
  destfile = paste0("map1879", ".geojson"))

#map <- readOGR("map1879.geojson", "OGRGeoJSON") # works
map <- readOGR("map1879.geojson", "OGRGeoJSON", p4s = "+proj=longlat +datum=WGS84")
#map@proj4string

# to merge with data.frame from SpatialPolygonsDataFrame it is advised to 
# take out data.frame, create sorting ID, do the merge and put it back in sorted according to ID.  
temp <- map@data
temp$area_km2 <- gArea(map, byid = TRUE)*10000
temp$sorder <- c(1:length(temp$id))
temp <- merge(temp, res,
               by.x = "amsterdamcode",
               by.y = "amsterdam_code",
               all.x = TRUE, sort = FALSE)
temp$houses_km2 <- round(temp$tot/(temp$area_km2),2)
temp <- temp[order(temp$sorder), ]
temp$total_nr_houses <- temp$tot

# overwrite map@data with merged data.frame
map@data <- temp
rm(temp)
#writeOGR(obj= map, dsn = "./map1879_withdata", layer = "", 
#         driver='GeoJSON') 
mapgeo <- toGeoJSON(data = map, dest = "./", name = "map1879houses")

# plot the data
# determine cutpoints (using descriptive statistics)
cuts = round(quantile(map@data$houses_km2, probs = seq(0, 1, 0.05), na.rm = TRUE), 0)
cuts[1]<-0 # ----- for this example make first cut zero

sty<-styleGrad(prop="houses_km2", breaks=cuts, right=FALSE, 
               style.par="col", style.val=rev(heat.colors(21)), 
               leg="Nr. of inhabited houses per square km", lwd=1)
popup<-c("name", "amsterdamcode", "houses_km2", "total_nr_houses", "area_km2") 

#### create map
# first add historical basemap
addBaseMap(
  name="nl1800", 
  title="nl1800", 
  url="http://maps.nypl.org/warper/maps/tile/7398/{z}/{x}/{y}.png",
  options=list(
    attribution='&copy; <a href="http://maps.nypl.org/warper/", target=
      "_blank">NYPL Map Warper</a>'
  )
)


CEDARmap <- leaflet(mapgeo, incl.data = TRUE, popup=popup, 
                 style = sty, base.map = c("mqsat", "nl1800"))





# plot map
CEDARmap # plot the map in browser

# EOF

