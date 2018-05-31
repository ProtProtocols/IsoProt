"""
This file contains the complete python code to display a user interface in a
Jupyter cell and allows user to perform an MS/MS database search.

All searchGUI and PeptideShaker functions used in this workflow are called and
managed through this file.
"""

import os
import time
import typing
import psutil
import subprocess


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


class TaskRunner:
    def __init__(self, cwd):
        self.cwd = cwd

    def __call__(self, name, param_list, check_for_file=None, **kwargv):
        print("Start:", name)

        start_time = time.time()
        task = subprocess.run(param_list, cwd=self.cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **kwargv)

        if task.returncode != 0:
            print(task.stdout)
            raise Exception("Error: %s failed" % name)

        if check_for_file:
            if not os.path.isfile(check_for_file):
                raise Exception("Error: Result fle '%s' not found." % check_for_file)

        run_time = time.time() - start_time
        # TODO explore better formating
        run_time_str = "%d sec" % run_time if run_time < 60 else "%d:%d min" % (run_time // 60, run_time % 60)
        print("    Completed in %s" % run_time_str)


def run(work_dir: str,
        fasta_db_path: str,
        generate_decoy: bool,
        spectra_dir: str,
        precursor_tolerance: float,
        fragment_tolerance: float,
        labelling: str,
        labelling_method: str,
        missed_cleavages: int,
        var_ptms: typing.Tuple[str, ...],
        fixed_ptms: str,
        exp_design_file_path: str #TODO
        ):
    """
    Generate the decoy database, run the search, and convert the search engine results to TSV files.

    :return: tsv_result_file_path
    """

    # for k, v in (
    #         ("work_dir           ,", work_dir),
    #         ("fasta_db           ,", fasta_db),
    #         ("generate_decoy     ,", generate_decoy),
    #         ("spectra_dir        ,", spectra_dir),
    #         ("precursor_tolerance,", precursor_tolerance),
    #         ("fragment_tolerance ,", fragment_tolerance),
    #         ("labelling          ,", labelling),
    #         ("labelling_method   ,", labelling_method),
    #         ("missed_cleavages   ,", missed_cleavages),
    #         ("var_ptms           ,", var_ptms),
    #         ("fixed_ptms         ,", fixed_ptms),
    # ):
    #     print(k, v)
    #
    # print("=======================")

    # function to callculate paths local to work_dir
    def get_path(*args):
        return os.path.join(work_dir, *args)

    # initialise work_dir for subprocess.run
    task_run = TaskRunner(work_dir)

    # get the free memory in MB
    free_mem = round(psutil.virtual_memory().available / 1024 / 1024)
    # if there's more than 1G available, leave 1G for other tasks
    if free_mem > 1000:
        free_mem -= 1000

    # create the directory paths to work in
    peaklist_abspath = os.path.abspath(spectra_dir)
    if not os.path.isdir(peaklist_abspath):
        raise Exception("Invalid peak list directory selected: " + peaklist_abspath + " does not exist.")

    peptide_shaker_jar_path = "/home/biodocker/bin/PeptideShaker-1.16.17/PeptideShaker-1.16.17.jar"
    searchgui_jar_path = "/home/biodocker/bin/SearchGUI-3.2.20/SearchGUI-3.2.20.jar"

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
    mgf_filenames = [os.path.join(peaklist_abspath, f) for f in os.listdir(peaklist_abspath) if
                     f[-4:].lower() == ".mgf"]
    adapt_mgf_titles(mgf_filenames)
    print(mgf_filenames)

    print("Extracting reporter peaks...")
    filter_mgf_peaks(mgf_filenames)

    # -------------------------------------
    # Generate the decoy database

    if generate_decoy:
        print("Creating decoy database...")

        # create the decoy database
        subprocess.run(["java", "-Xmx%sM" % free_mem,
                        "-cp", searchgui_jar_path, "eu.isas.searchgui.cmd.FastaCLI",
                        "-in", fasta_db_path,
                        "-decoy"],
                       check=True, cwd=work_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # get the filename of the decoy database
        database_file = os.path.abspath(fasta_db_path)[:-6] + "_concatenated_target_decoy.fasta"
    else:
        # simply use the selected database file
        database_file = os.path.abspath(fasta_db_path)

    if not os.path.isfile(database_file):
        raise Exception("Failed to find generated decoy database")

    # ---------------------------------------------
    # Create the search parameter file

    # path to resulting parameter file
    param_file = get_path("search.par")

    # remove any old parameters
    if os.path.isfile(param_file):
        os.remove(param_file)

    search_args = [
        "java", "-Xmx%sM" % free_mem,
        "-cp", searchgui_jar_path, "eu.isas.searchgui.cmd.IdentificationParametersCLI",
        "-out", param_file,
        "-prec_tol", str(precursor_tolerance),
        "-frag_tol", str(fragment_tolerance),
        "-db", database_file,
        "-fixed_mods", "%s,%s" % (labelling, fixed_ptms),  # TODO: labelling cannot always be set as fixed mod???
        "-mc", str(missed_cleavages),
    ]

    # add variable modofications to search_args
    if len(var_ptms) > 0 or ("Y variable" in labelling_method):
        var_mod_list = []

        for var_mod in var_ptms:
            if var_mod == "Phosphorylation of STY":
                var_mod_list += ["Phosphorylation of S", "Phosphorylation of T", "Phosphorylation of Y"]
            else:
                var_mod_list.append(var_mod)

        if labelling_method == "iTRAQ4 (Y variable)":
            var_mod_list.append("iTRAQ 4-plex of Y")
        if labelling_method == "iTRAQ8 (Y variable)":
            var_mod_list.append("iTRAQ 8-plex of Y")

        search_args.append("-variable_mods")
        search_args.append(",".join(var_mod_list))

    task_run("Creating serach parameter file",
             search_args,
             check_for_file=param_file,
             check=True
             )

    # ------------------------------------------------
    # Run the search

    # TODO: create list of spectrum files - or the folder
    spectrum_files = peaklist_abspath
    task_run("SearchCLI",
             ["java", "-Xmx%sM" % free_mem,
              "-cp", searchgui_jar_path, "eu.isas.searchgui.cmd.SearchCLI",
              "-spectrum_files", spectrum_files,
              "-output_folder", work_dir,
              "-id_params", param_file,
              "-xtandem", "0",
              "-msgf", "1",
              "-comet", "0",
              "-ms_amanda", "0",
              "-myrimatch", "0",
              "-andromeda", "0",
              "-omssa", "0",
              "-tide", "0"],
             universal_newlines=True
             )

    # -------------------------------------------------
    # Run PeptideShaker

    peptide_shaker_result_file_path = get_path("experiment.cpsx")
    task_run("PeptideShakerCLI processing",
             ["java", "-Xmx%sM" % free_mem,
              "-cp", peptide_shaker_jar_path, "eu.isas.peptideshaker.cmd.PeptideShakerCLI",
              "-useGeneMapping", "0",
              "-experiment", "experiment1",
              "-sample", "test",
              "-replicate", "1",
              "-identification_files", work_dir,
              "-out", peptide_shaker_result_file_path,
              "-id_params", param_file,
              "-spectrum_files", spectrum_files],
             check_for_file=peptide_shaker_result_file_path,
             universal_newlines=True
             )

    # ---------------------------------------------------
    # create TSV output files

    tsv_result_file_path = get_path("experiment1_test_1_Extended_PSM_Report.txt")
    task_run("ReportCLI (conversion to .tsv)",
             ["java", "-Xmx%sM" % free_mem,
              "-cp", peptide_shaker_jar_path, "eu.isas.peptideshaker.cmd.ReportCLI",
              "-in", peptide_shaker_result_file_path,
              "-out_reports", work_dir,
              "-reports", "8"],
             check_for_file=tsv_result_file_path,
             universal_newlines=True
             )

    print("Search Done.")

