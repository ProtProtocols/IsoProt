"""
This file contains the complete python code to display a user interface in a
Jupyter cell and allows user to perform an MS/MS database search.

All searchGUI and PeptideShaker functions used in this workflow are called and
managed through this file.
"""

import ipywidgets as widgets
from ipywidgets import VBox, Label
import os
import pandas as pd
from IPython.display import Javascript, display
import json

# import search implementation every time as we develope
import importlib
import search

importlib.reload(search)


class SearchUI:
    """
    Class used to manage the search specific user interface.
    """

    def __init__(self):
        """
        Initializes the SearchUI object and creates all user interface
        objects as member variables.
        """

        # working directory
        self.work_dir_select = widgets.Dropdown(options={'/data/': '/data/', 'Example files': '/home/biodocker/'},
                                                value='/home/biodocker/')
        self.work_dir_select.observe(
            lambda change: self.updateFastaFiles(change["new"]), type='change', names='name'
        )

        # basic search settings
        self.precursor_tolerance = widgets.IntSlider(min=-10, max=30, step=1, value=10)
        self.fragment_tolerance = widgets.BoundedFloatText(min=0, max=200, value=0.05)
        self.fasta_db = widgets.Dropdown(options={"sp_human.fasta": "IN/sp_human.fasta"})

        self.generate_decoy = widgets.Checkbox(value=True, description="Generate decoy sequences")
        self.target_fdr = widgets.BoundedFloatText(min=0, max=1, value=0.01)

        # TODO  needs table to describe labeling formats
        self.labelling = widgets.Dropdown(options=
                                          {'TMT6': 'TMT 6-plex of K,TMT 6-plex of peptide N-term',
                                           'TMT10': 'TMT 10-plex of K,TMT 10-plex of peptide N-term',
                                           'iTRAQ4 (Y fixed)': 'iTRAQ 4-plex of K,iTRAQ 4-plex of Y,iTRAQ 4-plex of peptide N-term',
                                           'iTRAQ4 (Y variable)': 'iTRAQ 4-plex of K,iTRAQ 4-plex of peptide N-term',
                                           'iTRAQ8 (Y fixed)': 'iTRAQ 8-plex of K,iTRAQ 8-plex of Y,iTRAQ 8-plex of peptide N-term',
                                           'iTRAQ8 (Y variable)': 'iTRAQ 8-plex of K,iTRAQ 8-plex of peptide N-term'},
                                          value='TMT 10-plex of K,TMT 10-plex of peptide N-term')

        self.missed_cleavages = widgets.IntSlider(min=0, max=10, step=1, value=1)
        self.fixed_ptms = widgets.Dropdown(options=["Carbamidomethylation of C", "None"])

        # PTMs
        self.var_ptms = widgets.SelectMultiple(
            options=["Oxidation of M",
                     "Phosphorylation of STY",
                     "Acetylation of peptide N-term",
                     "Acetylation of protein N-term"],
            value=['Oxidation of M'])

        self.spectra_dir = widgets.Dropdown(options={"IN": "IN"})

        # basic stat input fields
        self.summarization_method = widgets.Dropdown(options=
                                                     {"Median of all PSMs": "median",
                                                      "Average of all PSMs": "average",
                                                      "Top 3 PSMs (Median)": "top3",
                                                      "iBAQ to combine peptides": "ibaq"},
                                                     value='ibaq')
        self.min_protein_psms = widgets.IntSlider(min=0, max=10, step=1, value=1)
        self.use_ptms_for_quant = widgets.Checkbox(value=True, description="Use PTMs for quantification")

        # button to show experimental design
        self.exp_des_button = widgets.Button(
            description='Enter design',
            disabled=False,
            button_style='',  # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Enter experimental design',
            icon='check'
        )

        self.exp_des_button.on_click(lambda _: self.show_exp_design())

        self.expDesignUI = ExpDesignUI(self)

    def get_work_dir(self):
        return os.path.abspath(os.path.join(self.work_dir_select.value, "OUT"))

    def get_labelling_method(self):
        return list(self.labelling.options.keys())[self.labelling.index]

    def show_exp_design(self):
        """
        Display the experimental design dialog. This function is called
        through the button at the end of the SearchUI dialog
        """

        # disable the exp_design button and the labelling method
        self.exp_des_button.disabled = True
        self.labelling.disabled = True
        self.work_dir_select.disabled = True

        # self.tab.selected_index = 1
        display(self.expDesignUI.get_root_widget())

    def updateFastaFiles(self, workdir):
        """
        Update the drop-down list that lists all available FASTA files found in the
        current input directory.]
        :param workdir: The current working directory used to search for FASTA files.
        """
        # get all FASTA files
        fasta_files = [file for file in os.listdir(workdir)
                               if file.endswith(".fasta") and ('decoy' not in file)]

        # also search all subdirectories for FASTA files
        for d in os.listdir(workdir):
            d_path = os.path.join(workdir, d)
            if os.path.isdir(d_path) and d[0] != ".":
                fasta_files += [os.path.join(d, file) for file in os.listdir(d_path)
                                                        if file.endswith(".fasta") and ('decoy' not in file)]

        # create the dict to add as values to the control
        file_list = dict()
        sel_value = None

        for f in fasta_files:
            file_list[f] = os.path.join(os.path.abspath(workdir), f)
            if sel_value is None:
                sel_value = os.path.join(os.path.abspath(workdir), f)

        self.fasta_db.options = file_list
        self.fasta_db.value = sel_value

        # update the list of possible peaklist directories
        directories = [d for d in os.listdir(workdir) if os.path.isdir(os.path.join(workdir, d)) and d[0] != "."]

        dir_list = dict()

        for d in directories:
            dir_list[d] = os.path.join(os.path.abspath(workdir), d)

        self.spectra_dir.options = dir_list

        if "IN" in dir_list:
            self.spectra_dir.value = dir_list["IN"]

    def display(self):
        """
        Displays the search user interface.
        """
        self.updateFastaFiles(self.work_dir_select.value)

        search_box = VBox([Label('Precursor tolerance (ppm):'), self.precursor_tolerance,
                           Label('Fragment ion tolerance (da):'), self.fragment_tolerance,
                           Label('Number of miscleavages;'), self.missed_cleavages,
                           Label('Further fixed modifications'), self.fixed_ptms,
                           Label('Further variable modifications (Hold Ctrl to select multiple)'), self.var_ptms,
                           Label('Fasta file (database, must NOT contain decoy sequences):'), self.fasta_db,
                           self.generate_decoy,
                           Label('Target (protein, peptide, and PSM) FDR:'), self.target_fdr,
                           Label('Quantification method:'), self.labelling,
                           Label('Summarization method:'), self.summarization_method,
                           Label('Minimum number of PSMs per protein:'), self.min_protein_psms,
                           self.use_ptms_for_quant,
                           Label('Working directory (existing files will be deleted!)'), self.work_dir_select,
                           Label('Folder for spectra files (files need to be mgf)'), self.spectra_dir,
                           Label('Note: When entering the experimental design, the working directory and '
                                 'labelling method can no longer be changed.'),
                           self.exp_des_button])

        # expDesign_box = self.expDesignUI.get_root_widget()
        # self.tab = widgets.Tab([search_box, expDesign_box])
        # self.tab.set_title(0, "Search Settigns")
        # self.tab.set_title(1, "Experiment Design")
        # ui = tab

        ui = search_box
        display(ui)

    def _ipython_display_(self):
        return self.display()

    def save_config(self, file):
        """
        Save all configurations set by the user into a JSON formatted
        text file.
        :param: file: The name of the target file to use. Will be overwritten if it exists.
        """
        search_config = dict()
        search_config["work_dir"] = self.work_dir_select.value
        search_config["precursor_tolerance"] = self.precursor_tolerance.value
        search_config["fragment_tolerance"] = self.fragment_tolerance.value
        search_config["fasta_file"] = self.fasta_db.value
        search_config["generate_decoy"] = self.generate_decoy.value
        search_config["quantification_method"] = self.labelling.value
        search_config["missed_cleavages"] = self.missed_cleavages.value
        search_config["fixed_mods"] = self.fixed_ptms.value
        search_config["var_mods"] = self.var_ptms.value
        search_config["summarization_method"] = self.summarization_method.value
        search_config["min_protein_psms"] = self.min_protein_psms.value
        search_config["use_ptms_for_quant"] = self.use_ptms_for_quant.value
        search_config["target_fdr"] = self.target_fdr.value

        json_string = json.dumps(search_config)

        with open(file, "w") as writer:
            writer.write(json_string + "\n")


class ExpDesignUI:
    def __init__(self, searchUI: SearchUI):
        """
        Generates all use interface objects as member variables.

        :param searchUI: Parent user interface
        """

        self.searchUI = searchUI

        self.result_file_path = os.path.join(searchUI.get_work_dir(), "exp_design.tsv")

        # always expect two groups
        self.group1_name = widgets.Text(placeholder="Treatment", description="Group 1:")
        self.group2_name = widgets.Text(placeholder="Control", description="Group 2:")

        self.channels = {
            'TMT6': ["126", "127", "128", "129", "130", "131"],
            'TMT10': ["126", "127N", "127C", "128N", "128C", "129N", "129C", "130N", "130C", "131"],
            'iTRAQ4': ["114", "115", "116", "117"],
            'iTRAQ8': ["113", "114", "115", "116", "117", "118", "119", "121"]
        }

        # removed everything in string labellign_technique after space
        labelling_method = searchUI.get_labelling_method()
        if labelling_method.split(" ")[0] not in self.channels:
            raise Exception("Unknown labelling technique: '" + labelling_method + "'")

        self.labelling_technique = labelling_method.split(" ")[0]

        # generate the textfields for the channels
        self.channel_names = list()

        for channel in self.channels[self.labelling_technique]:
            self.channel_names.append(widgets.Text(description=channel, placeholder="Sample " + channel))

        # add select boxes to select the experimental group
        self.group_selects = list()

        for channel in self.channels[self.labelling_technique]:
            self.group_selects.append(widgets.Dropdown(options=["Group 1", "Group 2"], value="Group 1"))

        self.save_button = widgets.Button(
            description='Save design',
            disabled=False,
            button_style='',  # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Save the experimental design',
            icon='check'
        )

        self.save_button.on_click(self.save_design)

        self.search_button_visible = False

    def get_root_widget(self):
        """
        Displays the user interface to enter the experimental design.
        """
        widget_list = [widgets.Label("Treatment group names:"), self.group1_name, self.group2_name,
                       widgets.Label("Sample names (per channel):")]

        for i in range(0, len(self.channel_names)):
            widget_list.append(widgets.HBox([self.channel_names[i], self.group_selects[i]]))

        widget_list.append(self.save_button)

        widget_box = VBox(widget_list)

        return widget_box

    def save_design(self, button):
        """
        Save the experimental design as a TSV file.
        :param button: The button that triggered the function.
        """
        # get all names
        sample_names = [s.value if s.value != "" else s.placeholder for s in self.channel_names]
        sample_group = [g.value for g in self.group_selects]
        channel_names = self.channels[self.labelling_technique]

        # TODO: make sure all sample names are filled in

        # replace the group names
        for i in range(0, len(sample_group)):
            if sample_group[i] == "Group 1":
                sample_group[
                    i] = self.group1_name.value if self.group1_name.value != "" else self.group1_name.placeholder
            elif sample_group[i] == "Group 2":
                sample_group[
                    i] = self.group2_name.value if self.group2_name.value != "" else self.group2_name.placeholder

        design_data = pd.DataFrame(
            data={'channel': channel_names, 'sample_name': sample_names, 'sample_group': sample_group},
        )

        design_data.to_csv(path_or_buf=self.result_file_path, sep="\t", index=False)

        # add the run search button
        if not self.search_button_visible:
            self.search_button = widgets.Button(
                description='Run search',
                disabled=False,
                button_style='',  # 'success', 'info', 'warning', 'danger' or ''
                tooltip='Run the search',
                icon='check'
            )

            self.search_button.on_click(
                lambda _: self.run_search(self.searchUI, self.result_file_path)
            )

            search_box = VBox([self.search_button])
            display(search_box)

            self.search_button_visible = True

    def run_search(self, searchUI, exp_design_file_path):


        # make sure all required fields were selected
        if searchUI.work_dir_select.value is None:
            print("Error: No working directory selected")
            return

        if searchUI.fasta_db.value is None:
            print("Error: No FASTA file selected")
            return

        # disable previous steps
        self.search_button.disabled = True
        self.save_button.disabled = True

        # Save the settings
        work_dir = os.path.abspath(os.path.join(searchUI.work_dir_select.value, "OUT"))
        searchUI.save_config(os.path.join(work_dir, "search_settings.json"))


        search.run(work_dir
                   , searchUI.fasta_db.value
                   , searchUI.generate_decoy.value
                   , searchUI.spectra_dir.value
                   , searchUI.precursor_tolerance.value
                   , searchUI.fragment_tolerance.value
                   , searchUI.labelling.value
                   , searchUI.get_labelling_method()
                   , searchUI.missed_cleavages.value
                   , searchUI.var_ptms.value
                   , searchUI.fixed_ptms.value
                   , exp_design_file_path
                   )

        # create parameter list as input for R script
        global Rinput
        Rinput.clear()
        Rinput.extend( [
            searchUI.labelling.value, searchUI.spectra_dir.value, work_dir,
            searchUI.summarization_method.value, searchUI.min_protein_psms.value,
            searchUI.use_ptms_for_quant.value, searchUI.target_fdr.value
        ] )


        # add the new button to run the R scripts
        run_quant_button = widgets.Button(
            description="Run quantification and peptide inference",
            layout=widgets.Layout(width='30%'))

        run_quant_button.on_click(lambda _: display(
            # Run the javascript code to launch the next cell
            Javascript(
                'IPython.notebook.execute_cell_range(IPython.notebook.get_selected_index()+1, IPython.notebook.get_selected_index()+6)')
        ))

        display(run_quant_button)


# global stuff
if __name__ == "__main__":
    Rinput = []
    ui = SearchUI()
    display(ui)



# def main():
#     global result_file, work_dir, peaklist_dir
#     peaklist_dir = os.path.abspath("IN")
#
# ui = SearchUI()
# display(ui)
#
#
# # -------------------
# # Code to create the UI
# # --------------------
# result_file = None
# work_dir = None
# peaklist_dir = None
# searchUI = None
# expDesignUI = None
# Rinput = None
#
# if __name__ == "__main__":
#     main()
