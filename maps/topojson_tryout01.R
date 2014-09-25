library(leafletR)

# adding map
addBaseMap(name = "nlgis", url = "")


install.packages('base64enc')
require(devtools)
require(base64enc)
install_github('ramnathv/rCharts@dev')
install_github('ramnathv/rMaps')
library(rMaps)
crosslet(
  x = "country", 
  y = c("web_index", "universal_access", "impact_empowerment", "freedom_openness"),
  data = web_index
)


library(leafletR)
library(jsonlite)
data1 <- fromJSON("http://node-128.dev.socialhistoryservices.org/api/maps?year=1812")
str(data1)
plot(data1)
q.map <- leaflet(data=data1)
data2 <- toJSON(data1)
q.map <- leaflet(data=data2)

leaflet2 <- function (data, dest, title, size, base.map = "osm", center, 
                      zoom, style, popup, incl.data = FALSE, overwrite = TRUE) 
{
  if (missing(data)) 
    data <- NA
  if (length(data) > 1) 
    for (n in 1:length(data)) {
      if (!is.na(data[[n]])) 
        #if (tolower(tail(strsplit(tail(strsplit(data[[n]], 
        #                                        "/")[[1]], 1), "[.]")[[1]], 1)) != "geojson") 
        #  stop("'data' requires GeoJSON files (file extension should be 'geojson')")
      suppressWarnings(if (require(RJSONIO, quietly = TRUE)) 
        if (!isValidJSON(data[[n]])) 
          stop("'data' is not a valid JSON file"))
    }
  else {
    if (!is.na(data)) {
      #if (tolower(tail(strsplit(tail(strsplit(data, "/")[[1]], 
      #                               1), "[.]")[[1]], 1)) != "geojson") 
      #  stop("'data' requires GeoJSON files (file extension should be 'geojson')")
      suppressWarnings(if (require(RJSONIO, quietly = TRUE)) 
        if (!isValidJSON(data)) 
          stop("'data' is not a valid JSON file"))
    }
  }
  if (missing(dest)) 
    dest <- getwd()
  dest <- gsub("\\\\", "/", dest)
  if (missing(title)) {
    if (any(is.na(data))) 
      title <- "map"
    else {
      if (length(data) == 1) 
        title <- gsub("_", " ", 
                      paste(head(strsplit(tail(strsplit(data, 
                                                                  "/")[[1]], 1), "[.]")[[1]], -1), collapse = "_"))
      else title <- "map"
    }
  }
  if (missing(size)) 
    size <- NA
  bm <- c("osm", "tls", "mqosm", "mqsat", "water", "toner")
  base.map <- bm[pmatch(base.map, bm)]
  if (any(is.na(base.map))) 
    stop("Invalid base.map")
  if (missing(center)) 
    center <- NA
  if (missing(zoom)) 
    zoom <- NA
  if (missing(style)) 
    style <- NA
  if (missing(popup)) 
    popup <- NA
  if (any(!is.na(style))) {
    if (class(style) == "list") {
      for (i in 1:length(style)) if (class(style[[i]]) != 
                                       "leafletr.style") 
        stop("At least one style object not recognized")
    }
    else if (class(style) != "leafletr.style") 
      stop("Style object not recognized")
  }
  if (length(data) > 1 && !is.na(style)) 
    if (length(style) < length(data) || !is.list(style)) 
      stop("Number of styles must correspond to number of data files")
  if (file.exists(file.path(dest, gsub(" ", "_", title))) && 
        !overwrite) 
    stop("Abort - file already exists")
  if (!any(is.na(popup))) {
    if (is.list(popup)) {
      for (n in 1:length(popup)) if (length(popup[[n]]) == 
                                       1) 
        if (popup[[n]] == "*") 
          popup[[n]] <- getProperties(data[[n]], FALSE)
    }
    else {
      if (length(popup) == 1) 
        if (popup == "*") 
          popup <- getProperties(data[[1]], FALSE)
    }
  }
  dir.create(file.path(dest, gsub(" ", "_", title)), showWarnings = FALSE)
  if (any(!is.na(data)) && !incl.data) {
    for (n in 1:length(data)) file.copy(data[[n]], file.path(dest, 
                                                             gsub(" ", "_", title)), overwrite = overwrite)
  }
  if (any(is.na(data))) {
    center <- c(0, 0)
    zoom <- 2
  }
  filePath <- file.path(dest, gsub(" ", "_", title), paste0(gsub(" ", 
                                                                 "_", title), ".html"))
  leafletInt(data, path = filePath, title, size, base.map, 
             center, zoom, style, popup, incl.data)
  message("\nYour leaflet map has been saved under ", filePath)
  invisible(filePath)
}

library(Rmaps)
library(rgdal)
"GeoJSON" %in% ogrDrivers()$name
"TopoJSON" %in% ogrDrivers()$name






library(sp)
library(rgdal)

setwd(tempdir())
download.file('https://raw.github.com/oscarperpinan/solar/gh-pages/data/SIAR.csv', 'siar.csv', method='wget')
siar <- read.csv('siar.csv')
summary(siar)
siarSP <- SpatialPointsDataFrame(siar[,c(6, 7)], siar[,-c(6,7)])
writeOGR(siarSP, 'siar.geojson', 'siarSP', driver='GeoJSON')



library(maptools)
library(leafletR)
library(RColorBrewer)
setwd("/Users/richard/Dropbox/II/projects/nlgis2/maps/")
map <- leaflet(data="test.geojson")


library(rMaps)

maps = Datamaps$new()

maps$set(
  geographyConfig = list(
    dataUrl="http://node-128.dev.socialhistoryservices.org/api/maps?year=1812"
  ),
  
  scope = "states",
  setProjection = '#! function( element, options ) {
  var projection, path;
  projection = d3.geo.transverseMercator()
  .rotate([-27,-65,0])
  .scale(2000)
  .translate([element.offsetWidth / 2, element.offsetHeight / 2]);
  
  path = d3.geo.path().projection( projection );
  return {path: path, projection: projection};
  } !#'
)


library(rMaps)

maps = Datamaps$new()

maps$set(
  geographyConfig = list(
    dataUrl="/Users/richard/Downloads/subunits-ny.json"
  ),
  
  scope = 'subunits-ny',
  setProjection = '#! function( element, options ) {
   var projection, path;
   projection = d3.geo.Mercator()
    .rotate([-27,-65,0])
    .scale(1000)
    .translate([element.offsetWidth / 2, element.offsetHeight / 2]);

   path = d3.geo.path().projection( projection );
   return {path: path, projection: projection};
  } !#'
)
maps

#############################

# leafletR


############################
library(leafletR)
library(RCurl)
library(R)
data <- getURL("http://node-128.dev.socialhistoryservices.org/api/maps?year=1812&format=geojson")

leaflet(data = "/Users/richard/Downloads/nld_1812.geojson")
# file:///Users/richard/Dropbox/UU/projects/NL/r/nld_1812/nld_1812.html
leaflet(data = "/Users/richard/Downloads/nld_1812.geojson", popup="id",
        base.map = "mqsat")
t.map <- leaflet(data = "/Users/richard/Downloads/nld_1812.geojson", 
        popup="type",
        base.map = "mqsat")
browseURL(t.map)

maps


maps

library(leafletR)

data <- download.file(url = "http://node-128.dev.socialhistoryservices.org/api/maps?year=1812&format=geojson",
                      destfile = "nld_1812.geojson")
map <- leaflet("./nld_1812.geojson")
browseURL(map)
browseURL("http://www.r-project.org")

library(leafletR)
view.nlg <- function(year, name){
  ply <- download.file(url = paste0(paste0("http://node-128.dev.socialhistoryservices.org/api/maps?year=",
        year), "&format=geojson"),
                       destfile = paste0(name, ".geojson"))
  geomap <- leaflet(paste0("./", paste0(name, ".geojson")),
                    title = paste0("Netherlands - ", year))
  browseURL(geomap)      
}
view.nlg(year = 1972, name = "its_working")



llr2 <- function (data, dest, title, size, base.map = "osm", center, 
                  zoom, style, popup, incl.data = FALSE, overwrite = TRUE) 
{
  if (missing(dest)) 
    dest <- getwd()
  dest <- gsub("\\\\", "/", dest)
  if (missing(title)) {
    if (any(is.na(data))) 
      title <- "map"
    else {
      if (length(data) == 1) 
        title <- gsub("_", " ", paste(head(strsplit(tail(strsplit(data, 
                                                                  "/")[[1]], 1), "[.]")[[1]], -1), collapse = "_"))
      else title <- "map"
    }
  }
  if (missing(size)) 
    size <- NA
  bm <- c("osm", "tls", "mqosm", "mqsat", "water", "toner")
  base.map <- bm[pmatch(base.map, bm)]
  if (any(is.na(base.map))) 
    stop("Invalid base.map")
  if (missing(center)) 
    center <- NA
  if (missing(zoom)) 
    zoom <- NA
  if (missing(style)) 
    style <- NA
  if (missing(popup)) 
    popup <- NA
  if (any(!is.na(style))) {
    if (class(style) == "list") {
      for (i in 1:length(style)) if (class(style[[i]]) != 
                                       "leafletr.style") 
        stop("At least one style object not recognized")
    }
    else if (class(style) != "leafletr.style") 
      stop("Style object not recognized")
  }
  if (length(data) > 1 && !is.na(style)) 
    if (length(style) < length(data) || !is.list(style)) 
      stop("Number of styles must correspond to number of data files")
  if (file.exists(file.path(dest, gsub(" ", "_", title))) && 
        !overwrite) 
    stop("Abort - file already exists")
  if (!any(is.na(popup))) {
    if (is.list(popup)) {
      for (n in 1:length(popup)) if (length(popup[[n]]) == 
                                       1) 
        if (popup[[n]] == "*") 
          popup[[n]] <- getProperties(data[[n]], FALSE)
    }
    else {
      if (length(popup) == 1) 
        if (popup == "*") 
          popup <- getProperties(data[[1]], FALSE)
    }
  }
  dir.create(file.path(dest, gsub(" ", "_", title)), showWarnings = FALSE)
  if (any(!is.na(data)) && !incl.data) {
    for (n in 1:length(data)) file.copy(data[[n]], file.path(dest, 
                                                             gsub(" ", "_", title)), overwrite = overwrite)
  }
  if (any(is.na(data))) {
    center <- c(0, 0)
    zoom <- 2
  }
  filePath <- file.path(dest, gsub(" ", "_", title), paste0(gsub(" ", 
                                                                 "_", title), ".html"))
  leafletInt(data, path = filePath, title, size, base.map, 
             center, zoom, style, popup, incl.data)
  message("\nYour leaflet map has been saved under ", filePath)
  invisible(filePath)
}

