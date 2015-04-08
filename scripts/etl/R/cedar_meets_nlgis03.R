# File: cedar_meets_nlgis02.R
# Author: richard.zijdeman@iisg.nl
# Date: October 10, 2014
# Purpose: see whether you can retrieve data from CEDAR's SPARQLE endpoint and
#          plot them on map retrieved from NLGIS-2 API.
# Note: DATA SHOULD NOT BE INTERPRETED SUBSTANTIVELY (for debugging purposes only)
# Laste change: 
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

# prepare RDF data query
endpoint <- "http://lod.cedar-project.nl/cedar/sparql"

sparql_prefix <-
  "PREFIX qb: <http://purl.org/linked-data/cube#>
  PREFIX cedar: <http://lod.cedar-project.nl:8888/cedar/resource/>
  PREFIX maritalstatus: <http://bit.ly/cedar-maritalstatus#>
  PREFIX sdmx-dimension: <http://purl.org/linked-data/sdmx/2009/dimension#>
  PREFIX sdmx-code: <http://purl.org/linked-data/sdmx/2009/code#>
  PREFIX cedarterms: <http://bit.ly/cedar#>"

query <- paste(sparql_prefix, "select ?year ?location (SUM(?pop) AS ?total) FROM <urn:graph:cedar:release> WHERE {
  ?obs a qb:Observation.
  ?obs cedarterms:population ?pop.
  ?obs sdmx-dimension:refArea ?location .
  FILTER NOT EXISTS { 
  	?obs cedarterms:isTotal "1"^^<http://www.w3.org/2001/XMLSchema#integer>.
	}
	?slice a qb:Slice.
	?slice qb:observation ?obs.
    ?slice sdmx-dimension:refPeriod ?year.
} GROUP BY ?year ?location ORDER BY ?year ?location LIMIT 1000")

res <- SPARQL(endpoint,query)$results

# from website
sparql_prefix <-
  "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
  PREFIX cedar: <http://lod.cedar-project.nl:8888/cedar/resource/>
  PREFIX tablink: <http://bit.ly/cedar-tablink#>"

query <- paste(sparql_prefix, "SELECT ?sheet ?cell ?value FROM <urn:graph:cedar:raw-data> WHERE {
  ?seedcell a tablink:RowHeader .
  ?seedcell tablink:value "__seed_text__" .
  ?seedcell tablink:parentCell ?parent.
  ?cell a tablink:RowHeader .
  ?cell tablink:parentCell ?parent.
  ?cell tablink:value ?value .
  ?cell tablink:sheet ?sheet .
}")





# own query
sparql_prefix <-
  "PREFIX qb: <http://purl.org/linked-data/cube#>
PREFIX cedar: <http://lod.cedar-project.nl:8888/cedar/resource/>
PREFIX maritalstatus: <http://bit.ly/cedar-maritalstatus#>
PREFIX sdmx-dimension: <http://purl.org/linked-data/sdmx/2009/dimension#>
PREFIX sdmx-code: <http://purl.org/linked-data/sdmx/2009/code#>
PREFIX cedarterms: <http://bit.ly/cedar#>"

query <- paste(sparql_prefix, "SELECT ?year (SUM(?pop) AS ?total) FROM <urn:graph:cedar:release> WHERE {
  ?obs a qb:Observation.
	?obs maritalstatus:maritalStatus maritalstatus:married.
	?obs cedarterms:population ?pop.
	?obs sdmx-dimension:sex sdmx-code:sex-F.
	?slice a qb:Slice.
	?slice qb:observation ?obs.
	?slice sdmx-dimension:refPeriod ?year.
} ORDER BY ?year LIMIT 10")

res <- SPARQL(endpoint,query)$results


#### older stuff from version 0.1
sparql_prefix <- 
  "prefix qb: <http://purl.org/linked-data/cube#>
   prefix cedar: <http://lod.cedar-project.nl:8888/cedar/resource/>
   prefix cedarterms: <http://bit.ly/cedar#>
   prefix maritalstatus: <http://bit.ly/cedar-maritalstatus#>
   prefix sdmx-dimension: <http://purl.org/linked-data/sdmx/2009/dimension#>
   prefix sdmx-code: <http://purl.org/linked-data/sdmx/2009/code#>"

query <- paste(sparql_prefix, "select * where {
  ?obs a qb:Observation.
  ?obs cedar:population ?pop.
  ?obs sdmx-dimension:sex sdmx-code:sex-V.
  ?slice a qb:Slice.
  ?slice sdmx-dimension:refPeriod ?year .
  ?obs sdmx-dimension:refArea ?muni .
}") 

query2 <- paste(sparql_prefix, 'select * where {
  ?obs a qb:Observation .
  ?obs cedar:population ?pop .
  ?obs sdmx-dimension:sex sdmx-code:sex-V .
  ?slice a qb:Slice .
  ?slice sdmx-dimension:refPeriod ?year .
  ?slice cedarterms:censusType "VT" .
  ?obs sdmx-dimension:refArea ?muni .
}')
# note the use of single quotes for VT, within double quotes

res <- SPARQL(endpoint,query)$results
res.sub <- subset(res,year==1920)
res.sub1 <- data.table(res.sub)
# NB: duplicate muni's should not be the case I guess. adding them up:
res.sub2 <- res.sub1[, sum(pop), by = muni]
setnames(res.sub2, c("muni", "V1"), c("amsterdam_code", "total_women"))
res.sub2$amsterdam_code <- str_sub(res.sub2$amsterdam_code, -6, -2)
head(res.sub2)

# get map from NLGIS-2 project
download.file(
  "http://node-128.dev.socialhistoryservices.org/api/maps?year=1920&format=geojson",
  destfile = paste0("map1920", ".geojson"))

map <- readOGR("map1920.geojson", "OGRGeoJSON")

# to merge with data.frame from SpatialPolygonsDataFrame it is advised to 
# take out data.frame, do the merge and put it back in.  
temp <- map@data
temp$sorder <- c(1:length(temp$id))

temp2 <- merge(temp, res.sub2,
               by.x = "amsterdamcode",
               by.y = "amsterdam_code",
               all.x = TRUE, sort = FALSE)
temp3 <- temp2[order(temp2$sorder), ]

# overwrite map@data with merged data.frame
map@data <- temp3
writeOGR(map, "./map_CEDAR_women_1920.geojson", layer = "", 
         driver='GeoJSON') 

# plot the data
# determine cutpoints (using descriptive statistics)
summary(map@data$total_women)
cuts = c(473, 30950, 62620, 125000, 171200, 20460000)
cuts
sty<-styleGrad(prop="total_women", breaks=cuts, right=FALSE, style.par="col",
               style.val=rev(heat.colors(7)), 
               leg="Total nr. of women, 1920, DEBUGGING purpose ONLY", lwd=1)
popup<-c("name", "amsterdamcode", "total_women") 

# create map
CEDARmap <- leaflet("./map_CEDAR_women_1920.geojson", incl.data = TRUE, popup=popup, 
                 style = sty, base.map = "mqsat")
CEDARmap # plot the map in browser

# EOF
