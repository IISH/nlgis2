
rm(list=ls())
library(nlgis)
help(nlgis)

temp.data <- nlg.get(code = "BEV3", year = "1890") # retrieven population data for 1890
nlg.map(temp.data, 1890, "Population") # plot data (note: warning for removing duplicates)
