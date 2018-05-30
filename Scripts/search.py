"""
This file contains the complete python code to display a user interface in a
Jupyter cell and allows user to perform an MS/MS database search.

All searchGUI and PeptideShaker functions used in this workflow are called and
managed through this file.
"""

import os
import subprocess
import psutil

def adapt_mgf_titles(filenames):
    """
    This function changes all MGF titles to [filename].[spec index]

    :param: filenames: Filenames of the MGF files to change
    """
    for filename in filenames:
        with open(filename, "r") as reader:
            clean_name = os.path.basename(filename).replace(" ", "_")
            # MGF index reference in PSI standard is 1-based
            cur_index = 1

            with open(filename + ".tmp", "w") as writer:
                for line in reader:
                    if line[0:6] == "TITLE=":
                        writer.write("TITLE=" + clean_name + "." + str(cur_index) + "\n")
                        cur_index += 1
                    else:
                        writer.write(line)

        # backup the original file
        os.rename(filename, filename + ".org")
        os.rename(filename + ".tmp", filename)


def filter_mgf_peaks(filenames, min_mz=100, max_mz=150):
    """
    Removes all peaks from the passed mgf files that are below min_mz or
    above max_mz. The results are written to files with the same name but
    ".filtered" appended to the name.

    :param: filenames: List of filenames to process.
    :param: min_mz: Minimum m/z a peak must have to be kept
    :param: max_mz: Maximum m/z a peak may have to be kept
    """
    for filename in filenames:
        with open(filename, "r") as reader:
            with open(filename + ".filtered", "w") as writer:
                for line in reader:
                    # check if it's a peak
                    if line[0].isdigit():
                        sep_index = line.find(" ")
                        if sep_index < 0:
                            sep_index = line.find("\t")
                        if sep_index < 0:
                            raise Exception("Invalid peak definition found: " + line +
                                            ". Failed to filter file " + filename)

                        mz = float(line[:sep_index])

                        # ignore any non-matching peaks
                        if mz < min_mz or mz > max_mz:
                            continue

                    # copy the line
                    writer.write(line)


def run( work_dir: str
        , fasta_db
        , generate_decoy
        , spectra_dir
        , precursor_tolerance
        , fragment_tolerance
        , labelling
        , labelling_method
        , missed_cleavages
        , var_ptms
        , fixed_ptms
        , result_file=None
):
    """
    Generate the decoy database, run the search, and convert the search engine results to TSV files.

    :return: None
    """



    # get the free memory in MB
    free_mem = round(psutil.virtual_memory().available / 1024 / 1024)
    # if there's more than 1G available, leave 1G for other tasks
    if free_mem > 1000:
        free_mem -= 1000


    # create the directory paths to work in
    peaklist_dir = os.path.abspath(spectra_dir)

    if not os.path.isdir(peaklist_dir):
        raise Exception("Invalid peak list directory selected: " + peaklist_dir + " does not exist.")

    peptide_shaker_jar = "/home/biodocker/bin/PeptideShaker-1.16.17/PeptideShaker-1.16.17.jar"
    searchgui_jar = "/home/biodocker/bin/SearchGUI-3.2.20/SearchGUI-3.2.20.jar"
    exp_design_file = os.path.join(work_dir, "exp_design.tsv")

    # the searches should be performed in the "OUT" directory
    if not os.path.isdir(work_dir):
        os.mkdir(work_dir)
    else:
        print("Deleting existing files in " + str(work_dir))
        tmp_files = [f for f in os.listdir(work_dir) if os.path.isfile(os.path.join(work_dir, f))]
        for tmp_file in tmp_files:
            complete_name = os.path.join(work_dir, tmp_file)
            if os.path.isfile(complete_name):
                os.remove(complete_name)


    # -------------------------------------
    # Fix all MGF titles
    print("Adapting MGF titles...")
    mgf_filenames = [os.path.join(peaklist_dir, f) for f in os.listdir(peaklist_dir) if f[-4:].lower() == ".mgf"]
    adapt_mgf_titles(mgf_filenames)
    print(mgf_filenames)

    print("Extracting reporter peaks...")
    filter_mgf_peaks(mgf_filenames)

    # -------------------------------------
    # Generate the decoy database

    if generate_decoy:
        print("Creating decoy database...")

        # create the decoy database
        subprocess.run(["java", "-Xmx" + str(free_mem) + "M", "-cp", searchgui_jar,
                        "eu.isas.searchgui.cmd.FastaCLI", "-in", fasta_db, "-decoy"], check=True,
                       cwd=work_dir,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # get the filename of the decoy database
        database_file = os.path.abspath(fasta_db)[:-6] + "_concatenated_target_decoy.fasta"
    else:
        # simply use the selected database file
        database_file = os.path.abspath(fasta_db)

    if not os.path.isfile(database_file):
        raise Exception("Failed to find generated decoy database")

    # ---------------------------------------------
    # Create the search parameter file

    # build the arguments to create the parameter file
    param_file = os.path.join(work_dir, "search.par")

    # remove any old parameters
    if os.path.isfile(param_file):
        os.remove(param_file)

    search_args = list(["java", "-Xmx" + str(free_mem) + "M", "-cp", searchgui_jar,
                        "eu.isas.searchgui.cmd.IdentificationParametersCLI",
                        "-out", param_file])

    # precursor tolerance
    search_args.append("-prec_tol")
    search_args.append(str(precursor_tolerance))
    # fragment tolerance
    search_args.append("-frag_tol")
    search_args.append(str(fragment_tolerance))
    # fixed mods
    # TODO: labelling cannot always be set as fixed mod???
    fixed_mod_string = str(labelling) + "," + str(fixed_ptms)
    search_args.append("-fixed_mods")
    search_args.append(fixed_mod_string)
    # database
    search_args.append("-db")
    search_args.append(database_file)
    # missed cleavages
    search_args.append("-mc")
    search_args.append(str(missed_cleavages))

    if len(var_ptms) > 0 or ("Y variable" in labelling_method):
        search_args.append("-variable_mods")
        var_mod_list = list()

        for var_mod in var_ptms:
            if var_mod == "Phosphorylation of STY":
                var_mod_list += ["Phosphorylation of S", "Phosphorylation of T", "Phosphorylation of Y"]
            else:
                var_mod_list.append(var_mod)
        if labelling_method == "iTRAQ4 (Y variable)":
            var_mod_list.append("iTRAQ 4-plex of Y")
        if labelling_method == "iTRAQ8 (Y variable)":
            var_mod_list.append("iTRAQ 8-plex of Y")

        search_args.append(",".join(var_mod_list))

    # create the search parameter file
    print("Creating search parameter file...")
    # print(" ".join(search_args))
    subprocess.run(search_args, check=True, cwd=work_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if not os.path.isfile(param_file):
        raise Exception("Failed to create search parameters")

    # ------------------------------------------------
    # Run the search
    print("Running search...")
    # TODO: create list of spectrum files - or the folder
    spectrum_files = peaklist_dir
    print("  Searching files in " + spectrum_files)
    search_process = subprocess.run(["java", "-Xmx" + str(free_mem) + "M", "-cp", searchgui_jar,
                                     "eu.isas.searchgui.cmd.SearchCLI", "-spectrum_files", spectrum_files,
                                     "-output_folder", work_dir, "-id_params", param_file,
                                     "-xtandem", "0", "-msgf", "1", "-comet", "0", "-ms_amanda", "0",
                                     "-myrimatch", "0", "-andromeda", "0", "-omssa", "0", "-tide", "0"],
                                    check=False, cwd=work_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    universal_newlines=True)

    if search_process.returncode != 0:
        print(search_process.stdout)
        raise Exception("Search process failed.")

    print("Search completed.")

    # -------------------------------------------------
    # Run PeptideShaker
    print("Processing result using PeptideShaker...")
    peptide_shaker_result_file = os.path.join(work_dir, "experiment.cpsx")

    peptide_shaker_process = subprocess.run(["java", "-Xmx" + str(free_mem) + "M", "-cp", peptide_shaker_jar,
                                             "eu.isas.peptideshaker.cmd.PeptideShakerCLI",
                                             "-useGeneMapping", "0",
                                             "-experiment", "experiment1",
                                             "-sample", "test",
                                             "-replicate", "1",
                                             "-identification_files", work_dir,
                                             "-out", peptide_shaker_result_file,
                                             "-id_params", param_file,
                                             "-spectrum_files", spectrum_files],
                                            check=False, cwd=work_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                            universal_newlines=True)

    if peptide_shaker_process.returncode != 0:
        print(peptide_shaker_process.stdout)
        raise Exception("Failed to run PeptideShaker")

    if not os.path.isfile(peptide_shaker_result_file):
        raise Exception("Failed to process result file.")

    # ---------------------------------------------------
    # create TSV output files
    print("Converting result to TSV format...")
    conversion_process = subprocess.run(["java", "-Xmx" + str(free_mem) + "M", "-cp", peptide_shaker_jar,
                                         "eu.isas.peptideshaker.cmd.ReportCLI",
                                         "-in", peptide_shaker_result_file,
                                         "-out_reports", work_dir,
                                         "-reports", "8"],
                                        check=False, cwd=work_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        universal_newlines=True)

    if conversion_process.returncode != 0:
        print(conversion_process.stdout)
        raise Exception("Conversion process failed")

    result_file = os.path.join(work_dir, "experiment1_test_1_Extended_PSM_Report.txt")

    if not os.path.isfile(result_file):
        raise Exception("Error: Conversion failed")


    print("Search Done.")






