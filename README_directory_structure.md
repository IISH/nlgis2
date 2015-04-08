nlgis2 - directory structure
============================

+ data (contains all data files)
	- source (contains source (== original) data files (the way nlgis2 obtained them)
	- derived  (contains conversions, updates and expansions of original data files)
+ docs (contains all documentation)
+ graphs (contains graphical representations, i.e. maps, bar charts, etc.)
+ maps (Boonstra maps in its various formats, see readme.md inside dir)
+ presentations (contains all presentations of nlgis, only slides, not hands-on demo)
+ r_package (package that allows one to get data from the API and plot it on NLGIS maps (or plot other data)
+ scripts (contains all scripts)
	- etl (contains all extract, transform, load scripts)
		- hdng (scripts to extract .xls files from the historical database of dutch municipalties)
	- analyses (contain scripts to analyse data)
+ web
