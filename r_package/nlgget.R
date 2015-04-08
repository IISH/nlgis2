library(jsonlite)

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
    data.url <- gsub("&year=NA",  "", data.url)
    data.url <- gsub("&code=NA",  "", data.url)
    data.url <- gsub("&naam=NA",  "", data.url)
    data.url <- gsub(    "\\?&", "?", data.url)
  }
  
  print(data.url) #uncomment for test output of url
  # fromJSON(data.url)
}

