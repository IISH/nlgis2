\name{nlgis-package}
\alias{nlgis-package}
\alias{nlgis}
\docType{package}
\title{
Retrieve data from nlgis.nl and plot maps
}
\description{
This package makes it easy to download data from nlgis.nl and plot it as an interactive map. The data comprise of Dutch municipalities between 1812 and 1997 and the maps are based on historically accurate maps.}
\details{
\tabular{ll}{
Package: \tab nlgis\cr
Type: \tab Package\cr
Version: \tab 1.0\cr
Date: \tab 2014-12-01\cr
License: \tab GPL-3\cr
}
This package allows you to connect to the NLGIS API from within R. Use nlg.get() to retrieve data and nlg.map() to map data.
}
\author{
Richard L. Zijdeman

Maintainer: Richard Zijdeman <richard.zijdeman@iisg.nl>
}
\references{
http://nlgis.nl}
\keyword{ nlgis }
\seealso{
}
\examples{
# Examples to retrieve data
test1 <- nlg.get(amco = 11150, year = 1982) # all variables for Amsterdam in 1982
test2 <- nlg.get(code = "TXCU") # all years and municipalities for TXCU variable
test3 <- nlg.get(code = "TXCU", amco = 11150) # TXCU variable for all years, but just Amsterdam

# Example to plot data
temp.data <- nlg.get(code = "BEV3", year = "1890") # retrieven population data for 1890
nlg.map(temp.data, 1890, "bev3_1890") # plot data (note: warning for removing duplicates)
}