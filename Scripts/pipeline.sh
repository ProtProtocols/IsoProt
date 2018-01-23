#!/bin/bash

function check_error {
    RETURN_CODE="$1"
    MSG="$2"

    if [ "${RETURN_CODE}" != "0" ]; then
        echo "Error: $MSG"
        exit 1
    fi
}

# parse the parameters
while getopts "p:f:d:m:c:" opt; do
    case $opt in
        p)
            PRECURSOR_TOL="$OPTARG"
            ;;
        f)
            FRAGMENT_TOL="$OPTARG"
            ;;
        d)
            FASTA_DB="$OPTARG"
            ;;
        m)
            QUANT_METHOD="$OPTARG"
            ;;
        c)
            MISSED_CLEAV="$OPTARG"
            ;;
        :)
            echo "Error: Option -$OPTARG requires an argument."
            exit 1
            ;;
    esac
done

# TMT 10 mods
TMT_10="TMT 10-plex of K,TMT 10-plex of peptide N-term"
TMT_6="TMT 6-plex of K,TMT 6-plex of peptide N-term"

ITRAQ_4="iTRAQ 4-plex of K,iTRAQ 4-plex of Y,iTRAQ 4-plex of peptide N-term"
ITRAQ_8_FIXED="iTRAQ 8-plex of K, iTRAQ 8-plex of peptide N-term"
ITRAQ_8_VAR="iTRAQ 8-plex of Y"

# TODO: Adapt based on QUANT_METHOD settings
WORKDIR="pipeline-test"
FIXED_MODS="Carbamidomethylation of C,${TMT_10}"
VAR_MODS="Oxidation of M"

# TODO: Missing: replicate for peptide shaker, sample name for peptide shaker

# remove params
shift $((OPTIND-1))

# TODO: Make sure the required params were set

# ---- Change to workdir ----

if [ ! -d "${WORKDIR}" ]; then
    mkdir "${WORKDIR}"
    check_error $? "Failed to create working directory"
fi

for MGF_FILE in $@; do
    cp "${MGF_FILE}" "${WORKDIR}"
    check_error $? "Failed to copy peak list file to ${WORKDIR}"
done

# adapt FASTA path
FASTA_DB=`readlink -f "${FASTA_DB}"`

cd "${WORKDIR}"

# ---- Generate decoy ----
if [ ! -e "${FASTA_DB}" ]; then
    echo "Error: Cannot find FASTA database ${FASTA_DB}"
    exit 1
fi

java -cp /home/biodocker/bin/SearchGUI-*/SearchGUI-*.jar  eu.isas.searchgui.cmd.FastaCLI -in "${FASTA_DB}" -decoy

check_error $? "Failed to create decoy database"

DECOY_FASTA="${FASTA_DB%.*}_concatenated_target_decoy.fasta"

if [ ! -e ${DECOY_FASTA} ]; then
    echo "Failed to create decoy database"
    exit 1
fi

# ---- create parameter file for SearchGUI ----
java -cp /home/biodocker/bin/SearchGUI-*/SearchGUI-*.jar  eu.isas.searchgui.cmd.IdentificationParametersCLI -prec_tol ${PRECURSOR_TOL} -frag_tol ${FRAGMENT_TOL} -fixed_mods "${FIXED_MODS}"  -variable_mods "${VAR_MODS}" -db "${DECOY_FASTA}" -out search.par -mc ${MISSED_CLEAV}

check_error $? "Failed to create parameter file"

if [ ! -e "search.par" ]; then
    echo "Failed to create search parameters"
    exit 1
fi

# Run Search
# TODO: Explicitly specify peak list files
java -cp /home/biodocker/bin/SearchGUI-*/SearchGUI-*.jar eu.isas.searchgui.cmd.SearchCLI -spectrum_files ./  -output_folder ./  -id_params search.par -xtandem 0 -msgf 1 -comet 0 -ms_amanda 0 -myrimatch 0 -andromeda 0 -omssa 0 -tide 0

check_error $? "Search failed."


# ---- PeptideShaker ----
java -Xmx4G  -cp /home/biodocker/bin/PeptideShaker-*/PeptideShaker-*.jar eu.isas.peptideshaker.cmd.PeptideShakerCLI -experiment experiment1 -sample test -replicate 1 -identification_files "./"  -out ./experiment.cpsx -id_params search.par -spectrum_files './'

check_error $? "Failed to run PeptideShaker"

java -cp /home/biodocker/bin/PeptideShaker-*/PeptideShaker-*.jar eu.isas.peptideshaker.cmd.ReportCLI -in "experiment.cpsx" -out_reports "./" -reports "8"

# TEST FROM DOCKER: ./pipeline.sh -d crap.fasta -p 20 -f 0.05 -c 1 test.mgf
