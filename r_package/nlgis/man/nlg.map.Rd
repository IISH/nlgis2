\name{nlg.map}
\alias{nlg.map}
%- Also NEED an '\alias' for EACH other topic documented here.
\title{Map data from NLGIS
}
\description{
This function allows you to map data on Dutch municipalities between 1812 and 1997 using accurate historical boundaries.}
\usage{
nlg.map(df, year, filename, cuts = cuts.default)
}
%- maybe also 'usage' for other objects documented here.
\arguments{
  \item{df}{
A data.frame
}
  \item{year}{
The year of the historical map you want to plot data on.
}
  \item{filename}{
A filename you want to give to your map (no spaces allowed).
}
  \item{cuts}{
The number of cuts you want to use for the legend.
}
}
\details{
%%  ~~ If necessary, more details than the description above ~~
}
\value{
%%  ~Describe the value returned
%%  If it is a LIST, use
%%  \item{comp1 }{Description of 'comp1'}
%%  \item{comp2 }{Description of 'comp2'}
%% ...
}
\references{
%% ~put references to the literature/web site here ~
}
\author{
Richard L. Zijdeman
}
\note{
%%  ~~further notes~~
}

%% ~Make other sections like Warning with \section{Warning }{....} ~

\seealso{
%% ~~objects to See Also as \code{\link{help}}, ~~~
}
\examples{
# Example to plot data
temp.data <- nlg.get(code = "BEV3", year = "1890") # retrieven population data for 1890
nlg.map(temp.data, 1890, "bev3_1890") # plot data (note: warning for removing duplicates)
}
% Add one or more standard keywords, see file 'KEYWORDS' in the
% R documentation directory.
\keyword{ ~nlg.map}% __ONLY ONE__ keyword per line
