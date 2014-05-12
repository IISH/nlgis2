# File: rjson_tryout01.R
# Date: 2014-05-13 (YYYY-MM-DD)
# Author: richard.zijdeman@iisg.nl
# Laste change: -

# This is a first attempt to read JSON data from gemeentegeschiedenis.nl
# There's still a lot of hard coding, but the file provides a animated
# image of the borders of the city of Amersfoort over the past 200 years.

library(rjson)
library(animation)
json_file <- "http://www.gemeentegeschiedenis.nl/gemeentenaam/json/Amersfoort"
json_data <- fromJSON(paste(readLines(json_file), collapse=""))

years <- names(sapply(json_data$grenzen, "[[",1))
years
x.1812 <- sapply(json_data$grenzen$`1812`$features[[1]]$geometry$coordinates[[1]],
                 "[[",1)
y.1812 <- sapply(json_data$grenzen$`1812`$features[[1]]$geometry$coordinates[[1]],
                 "[[",2)
x.1895 <- sapply(json_data$grenzen$`1895`$features[[1]]$geometry$coordinates[[1]],
                 "[[",1)
y.1895 <- sapply(json_data$grenzen$`1895`$features[[1]]$geometry$coordinates[[1]],
                 "[[",2)
x.1941 <- sapply(json_data$grenzen$`1941`$features[[1]]$geometry$coordinates[[1]],
                 "[[",1)
y.1941 <- sapply(json_data$grenzen$`1941`$features[[1]]$geometry$coordinates[[1]],
                 "[[",2)
x.1960 <- sapply(json_data$grenzen$`1960`$features[[1]]$geometry$coordinates[[1]],
                 "[[",1)
y.1960 <- sapply(json_data$grenzen$`1960`$features[[1]]$geometry$coordinates[[1]],
                 "[[",2)
x.1974 <- sapply(json_data$grenzen$`1974`$features[[1]]$geometry$coordinates[[1]],
                 "[[",1)
y.1974 <- sapply(json_data$grenzen$`1974`$features[[1]]$geometry$coordinates[[1]],
                 "[[",2)

# #dev.off()
# plot(x.1974, y.1974, asp = 1, xlab = "X", ylab = "Y", pch = ".")
# polygon(x.1812, y.1812, col = rgb(1, 0, 0, 0.2))
# polygon(x.1895, y.1895, col = rgb(0, 1, 0, 0.2))
# polygon(x.1941, y.1941, col = rgb(0, 0, 1, 0.2))
# polygon(x.1960, y.1960, col = rgb(0, 1, 1, 0.2))
# polygon(x.1974, y.1974, col = rgb(1, 1, 0, 0.2))
# 
# 
# saveHTML({
#   for (i in 1:10) plot(runif(10), ylim = 0:1)
# })
# 
# dev.off()
saveHTML(expr = {
  plot(x.1812, y.1812, asp = 1, xlab = "X", ylab = "Y", pch = ".",
       main = "Amersfoort 1812-1894")
  polygon(x.1812, y.1812, col = rgb(1, 0, 0, 0.2))
  
  plot(x.1895, y.1895, asp = 1, xlab = "X", ylab = "Y", pch = ".",
       main = "Amersfoort 1894-1940")
  polygon(x.1812, y.1812, col = rgb(1, 0, 0, 0.2))
  polygon(x.1895, y.1895, col = rgb(0, 1, 0, 0.2))
  
  plot(x.1941, y.1941, asp = 1, xlab = "X", ylab = "Y", pch = ".",
       main = "Amersfoort 1941-1959")
  polygon(x.1812, y.1812, col = rgb(1, 0, 0, 0.2))
  polygon(x.1895, y.1895, col = rgb(0, 1, 0, 0.2))
  polygon(x.1941, y.1941, col = rgb(0, 0, 1, 0.2))
  
  plot(x.1960, y.1960, asp = 1, xlab = "X", ylab = "Y", pch = ".",
       main = "Amersfoort 1960-1973")
  polygon(x.1812, y.1812, col = rgb(1, 0, 0, 0.2))
  polygon(x.1895, y.1895, col = rgb(0, 1, 0, 0.2))
  polygon(x.1941, y.1941, col = rgb(0, 0, 1, 0.2))
  polygon(x.1960, y.1960, col = rgb(0, 1, 1, 0.2))
  
  plot(x.1974, y.1974, asp = 1, xlab = "X", ylab = "Y", pch = ".",
       main = "Amersfoort 1974-1997")
  polygon(x.1812, y.1812, col = rgb(1, 0, 0, 0.2))
  polygon(x.1895, y.1895, col = rgb(0, 1, 0, 0.2))
  polygon(x.1941, y.1941, col = rgb(0, 0, 1, 0.2))
  polygon(x.1960, y.1960, col = rgb(0, 1, 1, 0.2))
  polygon(x.1974, y.1974, col = rgb(1, 1, 0, 0.2))
}, outdir = "./graphs/", htmlfile = "amersfoort.html", 
title = "Zwolle", description = "Change in municipality borders")


# EOF