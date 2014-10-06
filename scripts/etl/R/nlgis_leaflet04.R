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
  fromJSON("http://node-128.dev.socialhistoryservices.org/api/data?year=1937")

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


map@data <- merge(map@data, testdata.sub1,
                  by.x = "amsterdamcode",
                  by.y = "amsterdam_code",
                  all.x = TRUE)

# plot data the traditional way: ####
at = c(7,500,1000,3194, 2488, 10000, 10000)
col = rev(heat.colors(length(at)))

mapvalues <- spplot(map,"value", at = at, col.regions = col, 
                    cuts = length(at),
                    main=list(label="value of TK", cex=2))
mapvalues # works!

# plot data using leafletR #### 
XXXX NB XXXX change "naam" to "name"?
XXX writeOGR(map, "./mapTK4.geojson", layer = c("value", "naam", "amsterdamcode"), 
         driver='GeoJSON') 
# NB error upon overwrite

cuts = c(7,500,1000,3194, 2488, 10000, 10000)
sty<-styleGrad(prop="value", breaks=cuts, right=FALSE, style.par="col",
               style.val=rev(heat.colors(6)), leg="value TK 1977", lwd=1)
popup<-c("name", "value", "amsterdamcode")
lfmap <- leaflet("./mapTK.geojson", incl.data = TRUE, popup=popup, style = sty)

lfmap # displays map in browser
# click on area for popup
### NB!!!!!! names of muni's are wrong! values too?!

### It appears that the link between name and amsterdamcode is right,
### but that that the name and amsterdamcode are linked to the wrong polygons
### Checking with just the map:

download.file(
  "http://node-128.dev.socialhistoryservices.org/api/maps?year=1977&format=geojson",
  destfile = paste0("testmap3", ".geojson"))
popup<-c("name", "amsterdamcode")
lfmap2 <- leaflet("./testmap3.geojson", incl.data = TRUE, popup=popup)
lfmap2
# names are correct, including amsterdamcode, so something weird happens when
# merging in the file


### error option 2: file is converted when reading/writing with rgdal
# get map (and showmap using leaflet) ####
download.file(
  "http://node-128.dev.socialhistoryservices.org/api/maps?year=1977&format=geojson",
  destfile = paste0("testmap4", ".geojson"))

# mapdata <- fromJSON(
#   "http://node-128.dev.socialhistoryservices.org/api/maps?year=1977&format=geojson"
#   )

map = readOGR("testmap3.geojson", "OGRGeoJSON")
plot(map)
map@data[map@data$amsterdamcode == 11150, ]
# still checks out

# write out file and checking again:
writeOGR(map, "./mapTK6.geojson", layer = "", 
         driver='GeoJSON') 
# checking map: 
lfmap5 <- leaflet("./mapTK6.geojson", incl.data = TRUE, popup=popup)
lfmap5

# works like a charm... so the error is not in reading/writing with writeOGR

## new check is the error a result of merging?
testdata2 <- 
  fromJSON("http://node-128.dev.socialhistoryservices.org/api/data?year=1977")
data7 <- testdata2$data
data7[data7$amsterdam_code == 11150, ]
# so far so good.
testdata2.sub <- subset(testdata2$data, code == "TEPV", 
                       select = c("amsterdam_code","naam", 
                                  "value"))
testdata2.sub1 <- subset(testdata2.sub, !duplicated(amsterdam_code))
str(testdata2.sub1)
# NB: amsterdam_code is type character, while it is 'int' in map@data

# just proceeding to see what happens, but prolly need to correct this
map@data <- merge(map@data, testdata2.sub1,
                  by.x = "amsterdamcode",
                  by.y = "amsterdam_code",
                  all.x = TRUE)

head(map@data) ## code appears to be just fine
str(map@data) # amsterdamcode remains integer
writeOGR(map, "./mapTK7.geojson", layer = "", 
         driver='GeoJSON') 
# plot data the traditional way: ####
at = c(7,500,1000,3194, 2488, 10000, 10000)
col = rev(heat.colors(length(at)))

cuts = c(7,500,1000,3194, 2488, 10000, 10000)
sty<-styleGrad(prop="value", breaks=cuts, right=FALSE, style.par="col",
               style.val=rev(heat.colors(6)), leg="TK, stemmen op CPN, 1956", lwd=1)
popup<-c("name", "amsterdamcode", "value", "naam") # naam is from data


lfmap <- leaflet("./mapTK7.geojson", incl.data = TRUE, popup=popup, style = sty)
lfmap # now it's wrong again

mapvalues2 <- spplot(map,"value", at = at, col.regions = col, 
                    cuts = length(at),
                    main=list(label="value of TK", cex=2))
mapvalues2 # works!

spplot(map)
testdata2


### again ####
rm(list=ls())
## new check is the error a result of merging?
testdata3 <- 
  fromJSON("http://node-128.dev.socialhistoryservices.org/api/data?year=1937")
data8 <- testdata3$data
data8[data8$amsterdam_code == 11150, ]
# so far so good.
testdata3.sub <- subset(testdata3$data, code == "TXCP", 
                        select = c("amsterdam_code","naam", 
                                   "value"))
testdata3.sub1 <- subset(testdata3.sub, !duplicated(amsterdam_code))
str(testdata3.sub1)
# NB: amsterdam_code is type character, while it is 'int' in map@data
# changing this:
testdata3.sub1$amsterdam_code <- as.integer(testdata3.sub1$amsterdam_code)
str(testdata3.sub1)

# get map
download.file(
  "http://node-128.dev.socialhistoryservices.org/api/maps?year=1937&format=geojson",
  destfile = paste0("testmap8", ".geojson"))

# mapdata <- fromJSON(
#   "http://node-128.dev.socialhistoryservices.org/api/maps?year=1977&format=geojson"
#   )

map = readOGR("testmap8.geojson", "OGRGeoJSON")
#plot(map)
map@data[map@data$amsterdamcode == 11150, ]
# still checks out

temp <- map@data
temp$sorder <- c(1:length(temp$id))


# just proceeding to see what happens, but prolly need to correct this
temp2 <- merge(temp, testdata3.sub1,
                  by.x = "amsterdamcode",
                  by.y = "amsterdam_code",
                  all.x = TRUE, sort = FALSE)
temp3 <- temp2[order(temp2$sorder), ]

# overwrite map@data
map@data <- temp3
head(map@data) ## code appears to be just fine
writeOGR(map, "./mapTK11.geojson", layer = "", 
         driver='GeoJSON') 
# plot data the traditional way: ####

#col = rev(heat.colors(length(at)))

cuts = quantile(map@data$value, na.rm = TRUE)
sty<-styleGrad(prop="value", breaks=cuts, right=FALSE, style.par="col",
               style.val=rev(heat.colors(6)), leg="value TK 1937", lwd=1)
popup<-c("name", "amsterdamcode", "value", "naam") # naam is from data


lfmap <- leaflet("./mapTK10.geojson", incl.data = TRUE, popup=popup, style = sty)
lfmap # now it's wrong again

mapvalues3 <- spplot(map,"value", at = at, col.regions = col, 
                     cuts = length(at),
                     main=list(label="value of TK", cex=2))
mapvalues3 # works!

spplot(map)
testdata2