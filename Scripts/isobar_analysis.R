library(isobar)

# process the input files
max.fdr <- 0.01
#quant.method <- "iTRAQ8plexSpectra"
quant.method <- "TMT10plexSpectra"
class.labels <- c("A", "B", "C", "D", "E", "F", "G", "H", "I", "J")
args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 2) {
    stop("Usage: isobar_analysis.R [search_result] [mgf_files...]")
}

ident.file <- args[1]
mgf.files <- args[2:length(args)]

if (!file.exists(ident.file)) {
    stop("Error: Cannot find identification file ", ident.file)
}
for (mgf.file in mgf.files) {
    if (!file.exists(mgf.file)) {
        stop("Error: Cannot find MGF file ", mgf.file)
    }
}

# Convert SearchGUI output to isobar format
psms <- read.csv(ident.file, sep = "\t")

if (! "Decoy" %in% names(psms)) {
    stop("Error: No decoy information available in output file")
}

message("Loaded ", nrow(psms), " PSMs")

# ---- Confidence filter ----
psms <- psms[order(psms[, "Confidence...."], decreasing = T), ]
decoy.psms <- which(psms[, "Decoy"] == "1")

decoy.count <- 0

for (decoy.index in decoy.psms) {
    decoy.count <- decoy.count + 1
    target.count <- decoy.index - decoy.count

    cur.fdr <- (decoy.count * 2) / (decoy.count + target.count)

    if (cur.fdr > max.fdr) {
        # filter
        psms <- psms[1:decoy.index - 1,]
        break
    }
}

message("Filtered ", nrow(psms), " PSMs @ ", max.fdr, " FDR")

# ---- convert to isobar output ----
cols.to.save <- c("Protein.s.", "Sequence", "Spectrum.Title", "Variable.Modifications", "Confidence....", "D.score", "Validation", "Precursor.m.z.Error..ppm.", "Spectrum.File")

if (!all(cols.to.save %in% colnames(psms))) {
    stop("Error: Unexpected result format")
}

psms <- psms[, cols.to.save]
colnames(psms) <- c("accession", "peptide", "spectrum", "var_mod", "pepscore", "dscore", "validation", "precursor.mz.error.ppm", "file")

# TODO: add modif...
psms$modif <- ""

write.table(psms, file = "t.corr.csv", sep = "\t", row.names = F, quote = F)

# ---- isobar workflow ----
ib <- readIBSpectra(quant.method, "t.corr.csv", mgf.files, decode.titles = T)

ib <- correctIsotopeImpurities(ib)
ib <- normalize(ib)
noise.model <- NoiseModel(ib)

protein.ratios <- proteinRatios(ib, noise.model, combn.method = "versus.channel", cl = class.labels)
peptide.ratios <- peptideRatios(ib, noise.model, combn.method = "versus.channel", cl = class.labels)

saveRDS(protein.ratios, file = "protein.ratios.rds")
saveRDS(peptide.ratios, file = "peptide.ratios.rds")
