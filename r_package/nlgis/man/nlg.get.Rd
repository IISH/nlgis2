\name{nlg.get}
\alias{nlg.get}
%- Also NEED an '\alias' for EACH other topic documented here.
\title{
Retrieve data from the NLGIS website through the API.
}
\description{
This function allows you to connect to the NLGIS API and retrieve data from the
NLGIS website.
}
\usage{
nlg.get(year = NA, code = NA, name = NA, amco = NA, cbs = NA)
}
%- maybe also 'usage' for other objects documented here.
\arguments{
  \item{year}{
Define the year for which you want data (leave open if you want to retrieve all years)
}
  \item{code}{
Define the variable code (see http://nlgis.nl/index) (leave open if you want to retrieve all variables)
}
  \item{name}{
Define the name of the municipality (Amsterdam Code spelling) (leave open if you want to retrieve all municipalities)
}
  \item{amco}{
Define the Amsterdam Code of the municipality (leave open if you want to retrieve all municipalities)
}
  \item{cbs}{
Define the CBS municipality code (leave open if you want to retrieve all municipalities)
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
Richard L. Zijdeman}
\note{
%%  ~~further notes~~
}

%% ~Make other sections like Warning with \section{Warning }{....} ~

\seealso{
%% ~~objects to See Also as \code{\link{help}}, ~~~
}
\examples{
# Examples to retrieve data
test1 <- nlg.get(amco = 11150, year = 1982) # all variables for Amsterdam in 1982
test2 <- nlg.get(code = "TXCU") # all years and municipalities for TXCU variable
test3 <- nlg.get(code = "TXCU", amco = 11150)# TXCU variable for all years, but just Amsterdam
}
% Add one or more standard keywords, see file 'KEYWORDS' in the
% R documentation directory.
\keyword{ ~nlgis }% __ONLY ONE__ keyword per line
