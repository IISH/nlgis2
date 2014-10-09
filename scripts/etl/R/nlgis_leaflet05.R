# File: nlgis_leaflet05.R
# Date: Oct 6, 2014
# Author: richard.zijdeman@iisg.nl
# Last change: starting to work on functions to access api's

# clean workspace
rm(list=ls())

### attempt to use data and geojson api to plot results
library(leafletR)
library(jsonlite)
library(rgdal)
library(sp)

# get data
# somedata <- 
#   fromJSON("http://node-128.dev.socialhistoryservices.org/api/data?year=1937")
# 
somedata <- 
   fromJSON("http://node-128.dev.socialhistoryservices.org/api/data?year=1937&code=TXCU")


# function to get data ####
nlgget <- function(year, code, name) {
  year.add <- paste0("&year=", year)
  code.add <- paste0("&code=", toupper(code))
  name.add <- paste0("&naam=", toupper(name))
  url <- "http://node-128.dev.socialhistoryservices.org/api/data"
  
  if (is.na(year) & is.na(code) & is.na(name)){
    data.url <- url
  }
   else {
     url <-paste0(url, "?")
     data.url <- paste0(paste0(paste0(url,year.add),code.add),name.add)
     # fixing wrong entries:
     data.url <- gsub("&year=NA", "", data.url)
     data.url <- gsub("&code=NA", "", data.url)
     data.url <- gsub("&naam=NA", "", data.url)
     data.url <- gsub("\\?&",    "?", data.url)
   }
  
  #print(data.url) #uncomment for test output of url
  fromJSON(data.url)
}
# nlgget(year=1937, code = "TXCU", name = "BAFLO")



###############
#x
t2 <- nlgget(year=1937, code = "TxCU", name = "BaFLO")


nlgget(year=1978)
t.1978.adam      <- nlgget(year=1978, name = "AMSTERDAM")
t.1978.adam.txcu <- nlgget(year=1978, name = "Amsterdam", code = "TXCU")


nlgplot()





nlgget(12)


test.data <- nlgget()


temp <- nlgget()
nlgget("1937", "")
nlgget(12,"weirdass")




# select relevant subset
somedata.1 <- subset(somedata$data, code == "TXRK", 
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
