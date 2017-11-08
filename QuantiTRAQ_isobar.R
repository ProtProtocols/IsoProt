library(lattice)
library(stringr)
library(isobar)
library(mzID)
library(matrixStats)
library(venneuler)


# filenames
ident_file <- "iTRAQ_test_1_Default_PSM_Report.txt"
mgf_files <- list.files(".",pattern=".mgf$",full.names = T)


## Convert SearchGUI output to file format that can be processed by isobar
psms <- read.csv(ident_file,sep="\t")

names(psms)
names(psms) <- c("X","accession","sequence","AAs.Before","AAs.After", "position", "peptide","modif",
                 "fixed", "file","spectrum","spectrum.id","retention.time","exp.moz","charge",
                 "id.charge","theo.mass","isotope.num","precursor.error","pepprob","pepscore","dscore",
                 "confidence","validation")

# filter for confidence > 80, confident and doubtful PTMs accepted
psms <- psms[psms$confidence > 80 
             & !grepl("Random",psms$pepprob) & !grepl("Not Scored",psms$pepprob),]

write.table(psms[,c("accession","peptide","spectrum","modif","pepprob","pepscore","file")],"t.corr.csv",
            sep="\t",row.names = F,quote=F)


## General isobar workflow
ib <- readIBSpectra("iTRAQ8plexSpectra","t.corr.csv",mgf_files,decode.titles=T)

ib <- correctIsotopeImpurities(ib)
ib <- normalize(ib)
maplot(ib,channel1="114",channel2="115",ylim=c(0.1,10),main="before normalization")

noise.model <- NoiseModel(ib)

protein.ratios <- proteinRatios(ib,noise.model,cl=c("A","B","C","D","E","F","G","H"),combn.method = "versus.channel")
peptide.ratios <- peptideRatios(ib,noise.model,cl=c("A","B","C","D","E","F","G","H"),combn.method = "versus.channel")

# Reorder table
prot1 <- by(protein.ratios$lratio, protein.ratios$ac, function(x) x)
prot1 <- matrix(unlist(prot1),ncol=7,byrow=T,dimnames=list(row=names(prot1),col=1:7))
boxplot(prot1)
prot1 <- prot1[rowSums(is.na(prot1)) < 7,]

### reading data from workflow 2
W2 <- read.csv("../Workflow2/quantitation.tsv",sep="\t")
boxplot((W2[,12:18]-W2[,11]))
W2Pep <- W2[,1:10]
W2Prot <- W2[,c(1,20:27)]
W2Prot[,1] <- sub("\\|.*","",sub("sp\\|","",W2Prot[,1]))
W2Prot[W2Prot==-9] <- NA
W2Prot <- W2Prot[rowSums(is.na(W2Prot[,2:ncol(W2Prot)]))<8,]
boxplot(W2Prot[,2:ncol(W2Prot)])
# mean normalization + conversion to log10 scale
W2Prot <- cbind(W2Prot[,1],(W2Prot[,2:ncol(W2Prot)]-rowMeans(W2Prot[,2:ncol(W2Prot)], na.rm=T))/0.3)
# mean normalization
prot1 <- cbind(0,prot1)
prot1 <- prot1 - rowMeans(prot1,na.rm=T)


# W2Prot[,2:ncol(W2Prot)] <- t(t(as.matrix(W2Prot[,2:ncol(W2Prot)])) - colMedians(as.matrix(W2Prot[,2:ncol(W2Prot)]),na.rm=T))

length(intersect(as.character(W2Prot[,1]),rownames(prot1)))
# Venn of protein identifications
venn <- venneuler(rbind(cbind(as.character(rownames(prot1)),paste("Workflow 1:",nrow(prot1))),
                  cbind(as.character(W2Prot[,1]),paste("\n\nWorkflow 2:",nrow(W2Prot)))))
#

 venn$labels <- paste(venn$labels,c(length(pepsW1),length(pepsW2),length(pepsW3)),sep="\n")

plot(venn,main="Common protein identifications: 1742")


Merged <- merge(prot1, W2Prot, by.x=0, by.y=1,all=T)
colnames(Merged) <- c("accessions",paste(rep(c("W1","W2"),each=8),c(113,114,115,116,117,118,119,121)))
boxplot(Merged[,2:ncol(Merged)],las=2, ylab="Protein ratios vs mean")
for (i in 1:8)
  plot(Merged[,1+i],Merged[,9+i],cex=0.1, xlab="W1 protein ratios vs mean",ylab="W2 protein ratios vs mean",
       main=paste("iTRAQ",sub("W1 ","",colnames(Merged)[i+1])))
pca <- princomp(Merged[complete.cases(Merged),2:ncol(Merged)])
plot(pca$loadings,pch=c(16,16,16,16,17,17,17,17),col=rainbow(4)[rep(1:4,2)])
text(pca$loadings, names(Merged[,2:ncol(Merged)]),pos=1)

pairs(Merged[,2:ncol(Merged)],cex=0.2)
# levelplot(cor(Merged[,2:ncol(Merged)],use="na.or.complete"))

