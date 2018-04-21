options(repos = c(CRAN = "https://cran.rstudio.com"))
update.packages(ask=F)
source("https://bioconductor.org/biocLite.R")
biocLite(ask=F)
biocLite(c("isobar", "limma", "grimbough/Rhdf5lib", "sneumann/mzR","Bioconductor/S4Vectors","Bioconductor/IRanges","Bioconductor/BiocGenerics", "lgatto/MSnbase"))

