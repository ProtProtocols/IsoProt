options(repos = c(CRAN = "https://cran.rstudio.com"))
update.packages(ask=F)
install.packages("BiocManager")
#source("https://bioconductor.org/biocLite.R")
#biocLite(ask=F)
BiocManager::install(ask=F)

install.packages("rjson")
packages.to.install <- 
c("BiocGenerics","S4Vectors","IRanges","Rhdf5lib","mzR","limma","isobar", "MSnbase","plotly","reshape","qvalue")

for (package in packages.to.install) {
    BiocManager::install(package)
}

