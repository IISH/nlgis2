# File: nlgget01.R
# Date: 2014-10-20
# Author: richard.zijdeman@iisg.nl
# Last change: none so far

# load libraries
library(jsonlite)

# create nlgget funtion to query data from HDNG api

nlgget <- function(year = NA, code = NA, name = NA, amco = NA, cbs = NA) {
  #year.add <- paste0("&year=", year)
  code.add <- paste0("&code=", toupper(code))
  name.add <- paste0("&naam=", toupper(name))
  amco.add <- paste0("&amsterdam_code=", amco)
  cbs.add  <- paste0("&cbsnr=", cbs)
  url <- "http://node-128.dev.socialhistoryservices.org/api/data"
  
  if (is.na(year) & is.na(code) & is.na(name) & is.na(amco) &
        is.na(cbs)){
    data.url <- url
  }
  else {
    url <-paste0(url, "?")
    data.url <- paste0(paste0(paste0(paste0(url,code.add),
                                     name.add), amco.add), cbs.add)
    # fixing wrong entries:
    #data.url <- gsub("&year=NA",            "", data.url)
    data.url <- gsub("&code=NA",            "", data.url)
    data.url <- gsub("&naam=NA",            "", data.url)
    data.url <- gsub("&amsterdam_code=NA",  "", data.url)
    data.url <- gsub("&cbsnr=NA",           "", data.url)
    data.url <- gsub("\\?&",               "?", data.url)
  }
  
  #print(data.url) #uncomment for test output of url
  raw <- fromJSON(data.url)
  raw$data$amsterdam_code <- as.integer(raw$data$amsterdam_code)
  if (!(is.na(year))) raw$data <- raw$data[ which(raw$data$year == year), ]
  raw$data
  #print(year) #uncomment for test output of year
}

# some lines to test it (uncommment)
# test1 <- nlgget(amco = 11150, year = 1982)
# test2 <- nlgget(code = "TXCU")
# test3 <- nlgget(code = "TXCU", amco = 11150)



