from UI_main_window import Ui_MainWindow
from settings import Settings
from assign_groups import AssignGroups
from show_group import ShowGroup
from statistics import Statistics
from spectrum import EvaluateSpectrum

import core_functions as cf
import evaluation_functions as ef

from PySide2 import QtCore, QtGui, QtWidgets

import time
import os
import json
import sys
import functools
from datetime import date
import logging
from logging.handlers import RotatingFileHandler

import matplotlib.pylab as plt
import numpy as np
import pandas as pd
import math

import webbrowser

# import randomcolor
import matplotlib as mpl


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    """
    This class contains the logic of the program and is explicitly seperated
    from the UI classes. However, it is a child class of Ui_MainWindow.
    Important data structures in the class:
        - self.assigned_groups_df: dataframe that contains all information of the user assigned groups from the assign groups dialog
        - self.data_df: dataframe that contains all relevant data for each relevant device like voltage, current and pd_voltage. Furthermore, all calculation results are simply added to this dataframe.
        - self.files_df: dataframe that contains all relevant information to the files that is mostly extracted directly from the file names of all files present in a global folder


    """

    def __init__(self):
        """
        Initialise instance
        """
        super(MainWindow, self).__init__()
        self.setupUi(self)

        # -------------------------------------------------------------------- #
        # -------------------------- State Variables ------------------------- #
        # -------------------------------------------------------------------- #
        # Set some state variables that log the current state of the program

        # Logs if data has been saved already. If no folder was selected, yet
        # it is True
        self.data_saved = True

        # Logs if folder path was already selected
        self.folder_path_selected = False
        self.groups_assigned = False

        # Assigned groups that contain all information returned by the assign
        # group dialog
        self.assigned_groups_df = pd.DataFrame(
            columns=["group_name", "spectrum_path", "color"]
        )

        # Data that shall later be put into settings window
        self.measurement_parameters = cf.read_global_settings()

        self.measurement_parameters["pd_radius"] = math.sqrt(
            self.measurement_parameters["pd_area"] / math.pi
        )
        self.measurement_parameters["sq_sin_alpha"] = self.measurement_parameters[
            "pd_radius"
        ] ** 2 / (
            (self.measurement_parameters["pd_distance"] * 1e-3) ** 2
            + self.measurement_parameters["pd_radius"] ** 2
        )
        self.current_plot_type = "none"

        # -------------------------------------------------------------------- #
        # ------------------------------ General ----------------------------- #
        # -------------------------------------------------------------------- #

        # Update statusbar
        cf.log_message("Initialising Program")
        self.tabWidget.currentChanged.connect(self.changed_tab_widget)

        # Hide by default and only show if a process is running
        self.progressBar.hide()

        # -------------------------------------------------------------------- #
        # ------------------------ Top Menubar ------------------------------- #
        # -------------------------------------------------------------------- #
        self.actionOptions.triggered.connect(self.show_settings)

        self.actionOpen_Log.triggered.connect(lambda: cf.open_file("log.out"))

        # Open the documentation in the browser (maybe in the future directly
        # open the readme file in the folder but currently this is so much
        # easier and prettier)
        self.actionDocumentation.triggered.connect(
            lambda: webbrowser.open(
                "https://github.com/GatherLab/me-measurement/blob/main/README.md"
            )
        )
        # -------------------------------------------------------------------- #
        # -------------------------- Right Menubar --------------------------- #
        # -------------------------------------------------------------------- #
        self.eval_change_path_pushButton.clicked.connect(self.browse_folder)
        self.eval_assign_groups_pushButton.clicked.connect(self.assign_groups)
        self.eval_plot_groups_pushButton.clicked.connect(self.plot_groups)
        self.eval_plot_statistics_pushButton.clicked.connect(self.plot_statistics)
        self.eval_save_pushButton.clicked.connect(self.save_evaluated_data)

        # Set all buttons except for the change path pushButton to disable
        # until a folder was selected
        self.eval_assign_groups_pushButton.setEnabled(False)
        self.eval_plot_groups_pushButton.setEnabled(False)
        self.eval_plot_statistics_pushButton.setEnabled(False)
        self.eval_spectrum_analysis_pushButton.setEnabled(False)
        self.eval_save_pushButton.setEnabled(False)

        # -------------------------------------------------------------------- #
        # --------------------------- Setup Widget --------------------------- #
        # -------------------------------------------------------------------- #
        # self.sw_browse_pushButton.clicked.connect(self.browse_folder)

        # -------------------------------------------------------------------- #
        # --------------------- Set Standard Parameters ---------------------- #
        # -------------------------------------------------------------------- #

        # Set standard parameters for autotube measurement
        # self.aw_min_voltage_spinBox.setValue(-2)
        # self.aw_min_voltage_spinBox.setMinimum(-50)
        # self.aw_max_voltage_spinBox.setValue(5)

    # -------------------------------------------------------------------- #
    # ---------------------------- Load Folder --------------------------- #
    # -------------------------------------------------------------------- #
    def browse_folder(self):
        """
        Open file dialog to browse through directories
        """
        global_variables = cf.read_global_settings()

        self.global_path = QtWidgets.QFileDialog.getExistingDirectory(
            QtWidgets.QFileDialog(),
            "Select a Folder",
            global_variables["default_saving_path"],
            QtWidgets.QFileDialog.ShowDirsOnly,
        )

        # Now get the file paths for all files at top level in this folder
        self.file_names = cf.read_file_names(self.global_path)

        # Now check if there are some files and how many in the folder
        if len(self.file_names) == 0:
            cf.log_message("Couldn't find any files in the selected top level folder.")
        else:
            cf.log_message(
                "Found "
                + str(len(self.file_names))
                + " files at top level in the selected folder."
            )
            self.investigate_file_names(self.file_names)

            # Now set the folder path as selected and allow for assignment of groups
            self.folder_path_selected = True
            self.eval_assign_groups_pushButton.setEnabled(True)

    def investigate_file_names(self, file_names):
        """
        Go through the names of all files in file_names and extract some
        relevant information for the rest of the program
        """
        # First dissect the file names by splitting at each _
        # This returns normally 4 fields and if there are multiple scans it
        # returns a fifth one
        self.files_df = pd.DataFrame()

        dates = []
        batch_names = []
        jvl_file_names = []
        device_numbers = []
        pixel_numbers = []
        scan_number = []
        identifier = []

        for name in file_names:
            split_name = name.split("_")
            if len(split_name) == 5:
                # Right file name but only one scan
                if str(split_name[4].split(".")[0]) != "jvl":
                    continue
                jvl_file_names.append(name)
                dates.append(str(split_name[0]))
                batch_names.append(str(split_name[1]))
                device_numbers.append(int(split_name[2][1:]))
                pixel_numbers.append(int(split_name[3].split(".")[0][1:]))
                scan_number.append(1)
                identifier.append(split_name[2] + split_name[3].split(".")[0] + "s1")
            elif len(split_name) == 6:
                # If this is > first scan
                if str(split_name[4].split(".")[0]) != "jvl":
                    continue
                jvl_file_names.append(name)
                dates.append(str(split_name[0]))
                batch_names.append(str(split_name[1]))
                device_numbers.append(int(split_name[2][1:]))
                pixel_numbers.append(int(split_name[3][1:]))
                identifier.append(
                    split_name[2]
                    + split_name[3]
                    + "s"
                    + split_name[5].split(".")[0][1:]
                )
                scan_number.append(int(split_name[5].split(".")[0][1:]))
            else:
                # File name is not in the correct format
                cf.log_message(
                    "The file name does not follow the naming convention date_batch-name_d<no>_p<no>_<no>.csv"
                )
        if np.size(np.unique(batch_names)) > 1:
            cf.log_message(
                "The batch name does not match for all files. If there are different OLEDs with the same device number this could lead to a problem."
            )

        self.files_df["file_name"] = jvl_file_names
        self.files_df["device_number"] = device_numbers
        self.files_df["pixel_number"] = pixel_numbers
        self.files_df["scan_number"] = scan_number

        # Now set the identifier as index
        self.files_df = self.files_df.set_index(np.array(identifier))

        # return the maximum scan number in the investigated batch
        self.max_scan_number = np.max(scan_number)

        cf.log_message(
            "Found "
            + str(len(jvl_file_names))
            + " jvl files at top level in selected folder."
        )
        cf.log_message("Maximum scan number found: " + str(self.max_scan_number))

        # Now generate a dictionary containing the device numbers as keys and
        # an array of the pixel numbers as values
        # self.devices_and_pixels = {}

        # for i in np.unique(device_numbers):
        #     self.devices_and_pixels[i] = np.array(pixel_numbers)[
        #         np.where(np.array(device_numbers, dtype=int) == i)[0]
        #     ]

    # -------------------------------------------------------------------- #
    # -------------------------- Assign Groups --------------------------- #
    # -------------------------------------------------------------------- #

    def assign_groups(self):
        """
        Function that opens the assign group dialog and allows to assign groups
        """
        parameters = {
            "no_of_scans": self.max_scan_number,
            "device_number": np.unique(self.files_df["device_number"].to_list()),
            "assigned_groups_df": self.assigned_groups_df,
        }

        self.assign_groups_dialog = AssignGroups(parameters, self)
        self.assign_groups_dialog.show()
        button = self.assign_groups_dialog.exec_()

        # Now check if user pressed close or save
        if button == True:
            # Only select those files that's device numbers were entered by the user
            selected_files = self.files_df[
                np.logical_and(
                    self.files_df["device_number"].isin(
                        self.assigned_groups_df.index.to_numpy()
                    ),
                    self.files_df["scan_number"] == self.selected_scan,
                )
            ]
            # Now read in the jvl files for selected devices
            self.data_df = cf.read_multiple_files(
                [
                    self.global_path + "/" + file_name
                    for file_name in selected_files["file_name"]
                ],
                ["voltage", "current", "pd_voltage"],
                selected_files.index.to_list(),
                skip_row=10,
            )

            # Do a left join on the files_df to obtain the device numbers
            self.data_df["device_number"] = self.data_df.join(self.files_df)[
                "device_number"
            ]

            cf.log_message(
                "Found correct IVL data for " + str(self.data_df.index.to_list())
            )

            # Only read in spectra if they were selected for all groups
            # The evaluation can also be only done if spectra were selected. In
            # the future this check might be moved to the assign dialog
            # directly
            if not self.assigned_groups_df["spectrum_path"].isnull().any():
                # Now check if the spectra are simple spectra or angle resolved ones
                i = 0

                for spectrum_path in self.assigned_groups_df["spectrum_path"].to_list():
                    if (
                        spectrum_path.split("_")[-1].split(".")[0] == "gon-spec"
                        or spectrum_path.split("_")[-2] == "gon-spec"
                    ):
                        # Goniometer file
                        # Read in the angle resolved file
                        angle_resolved_spectrum = pd.read_csv(
                            spectrum_path, sep="\t", skiprows=3
                        )

                        # Extract the foward spectrum and save to self.spectrum_data_df
                        if not hasattr(self, "spectrum_data_df"):
                            self.spectrum_data_df = pd.DataFrame(
                                [
                                    [
                                        [
                                            angle_resolved_spectrum["wavelength"],
                                        ],
                                        [
                                            angle_resolved_spectrum["background"],
                                        ],
                                        [
                                            angle_resolved_spectrum["0.0"],
                                        ],
                                    ]
                                ],
                                columns=["wavelength", "background", "intensity"],
                                index=[self.assigned_groups_df.index.to_list()[i]],
                            )
                        else:
                            self.spectrum_data_df.append(
                                pd.DataFrame(
                                    [
                                        [
                                            [
                                                angle_resolved_spectrum["wavelength"],
                                            ],
                                            [
                                                angle_resolved_spectrum["background"],
                                            ],
                                            [
                                                angle_resolved_spectrum["0.0"],
                                            ],
                                        ]
                                    ],
                                    columns=["wavelength", "background", "intensity"],
                                    index=[self.assigned_groups_df.index.to_list()[i]],
                                )
                            )

                        # Calculate correction factors
                        correction_factors = ef.calculate_angle_correction(
                            angle_resolved_spectrum, 1
                        )
                    elif (
                        spectrum_path.split("_")[-1].split(".")[0] == "spec"
                        or spectrum_path.split("_")[-2] == "spec"
                    ):
                        # Regular spectrum file
                        self.spectrum_data_df = cf.read_multiple_files(
                            self.assigned_groups_df["spectrum_path"].to_list(),
                            ["wavelength", "background", "intensity"],
                            self.assigned_groups_df.index.to_list(),
                            skip_row=14,
                        )

                        cf.log_message(
                            "Spectrum data found for devices "
                            + str(self.spectrum_data_df.index.to_list())
                        )

                    else:
                        # Not a valid spectrum name
                        cf.log_message(
                            "Selected spectrum file does not have a valid name"
                        )
                    i += 1

                # Now do the evaluation and append to the data_df dataframe
                self.evaluate_jvl()
            else:
                cf.log_message(
                    "Can not evaluate data without spectrum files for all groups."
                )

            # Set variables that define the program's state
            self.groups_assigned = True
            self.eval_plot_groups_pushButton.setEnabled(True)
            self.eval_plot_statistics_pushButton.setEnabled(True)
            self.eval_spectrum_analysis_pushButton.setEnabled(True)
            self.eval_save_pushButton.setEnabled(True)
        else:
            cf.log_message("Group assignement aborted")

    def evaluate_jvl(self):
        """
        Do the jvl evaluation calculations
        """

        # Reading V(lambda), photodiode sensitivity, and CIE normcurves
        df_basic_data = pd.read_csv(
            "./calibration/BasicData - PDA100A2.txt",
            names=["wavelength", "v_lambda", "photodiode_sensitivity"],
            sep="\t",
        )
        df_norm_curves = pd.read_csv(
            "./calibration/NormCurves_400-800.txt",
            names=["wavelength", "na", "xcie", "ycie", "zcie"],
            sep="\t",
        )
        df_correction_data = pd.read_csv(
            "./calibration/CorrectionData.txt",
            names=["wavelength", "correction"],
            sep="\t",
        )
        df_basic_data["interpolated"] = np.interp(
            df_basic_data.wavelength,
            df_correction_data.wavelength,
            df_correction_data.correction,
        )

        # Add empty columns to our basic dataframes
        self.data_df["current_density"] = np.empty((len(self.data_df), 0)).tolist()
        self.data_df["luminance"] = np.empty((len(self.data_df), 0)).tolist()
        self.data_df["eqe"] = np.empty((len(self.data_df), 0)).tolist()
        self.data_df["luminous_efficiency"] = np.empty((len(self.data_df), 0)).tolist()
        self.data_df["current_efficiency"] = np.empty((len(self.data_df), 0)).tolist()
        self.data_df["power_density"] = np.empty((len(self.data_df), 0)).tolist()
        self.data_df["masked"] = np.repeat(False, len(self.data_df))

        self.spectrum_data_df["interpolated_intensity"] = np.empty(
            (len(self.spectrum_data_df), 0)
        ).tolist()
        self.spectrum_data_df["corrected_intensity"] = np.empty(
            (len(self.spectrum_data_df), 0)
        ).tolist()
        self.spectrum_data_df["minus_background"] = np.empty(
            (len(self.spectrum_data_df), 0)
        ).tolist()

        for index, row in self.data_df.iterrows():

            # Transform to SI units for calculations
            # df_jvl_data["current"] = df_jvl_data["current"] / 1000
            # df_jvl_data["current_density"] = df_jvl_data.current / (pixel_area * 1e-2)
            # df_jvl_data["absolute_current_density"] = abs(df_jvl_data.current_density)
            self.data_df.at[index, "current"] = list(np.array(row["current"]) / 1000)
            self.data_df.at[index, "current_density"] = list(
                np.array(row["current"])
                / (self.measurement_parameters["pixel_area"] * 1e-2)
            )

            # Load spectral data and df_background. The idea is  that if there is no specific df_spectrum file given, the program searches for files containing d<no> in their name that matches the d<no> in the jvl data file name
            # if not spectrum_file:
            #     dev_number = np.array(file_name.split("_"))[
            #         [
            #             bool(re.match("^[0123456789d]+$", i))
            #             for i in file_name.split("_")
            #         ]
            #     ][0]
            #     spectrum_file_name = np.array(spectra_file_names)[
            #         [dev_number in str_ for str_ in spectra_file_names]
            #     ][0]
            #     spectrum_file_path = root_directory + "spectra/" + spectrum_file_name
            # else:
            #     spectrum_file_path = root_directory + "spectra/" + spectrum_file

            # The df_background path is always the same
            # background_file_path = root_directory + "spectra/background.txt"

            # # Load background file
            # df_background = pd.read_csv(
            #     background_file_path,
            #     header=12,
            #     names=["wavelength", "counts"],
            #     sep="\t",
            # )

            # # Load actual spectrum file
            # df_spectrum = pd.read_csv(
            #     spectrum_file_path,
            #     header=12,
            #     names=["wavelength", "counts"],
            #     sep="\t",
            # )

            # Interpolate this data on basic data and save in separate data frame
            # df_corrected_spectrum = pd.DataFrame()

            # Interpolate spectra onto correct axis and subtract background
            self.spectrum_data_df.at[
                row["device_number"],
                "interpolated_intensity",
            ] = np.interp(
                df_basic_data.wavelength.to_list(),
                self.spectrum_data_df.loc[row["device_number"], "wavelength"],
                self.spectrum_data_df.loc[row["device_number"], "intensity"],
            )

            self.spectrum_data_df.at[
                row["device_number"],
                "minus_background",
            ] = self.spectrum_data_df.at[
                row["device_number"], "interpolated_intensity"
            ] - np.interp(
                df_basic_data.wavelength.to_list(),
                self.spectrum_data_df.loc[row["device_number"], "wavelength"],
                self.spectrum_data_df.loc[row["device_number"], "background"],
            )

            self.spectrum_data_df.at[row["device_number"], "corrected_intensity",] = (
                self.spectrum_data_df.loc[
                    row["device_number"],
                    "minus_background",
                ]
                * df_basic_data.interpolated
            )
            # df_corrected_spectrum["spectrum_intensity"] = np.interp(
            #     df_basic_data.wavelength, df_spectrum.wavelength, df_spectrum.counts
            # )
            # df_corrected_spectrum["background_int"] = background_int = np.interp(
            #     df_basic_data.wavelength, df_background.wavelength, df_background.counts
            # )

            # Do df_background subtraction
            # df_corrected_spectrum["spectrum_m_background"] = (
            #     df_corrected_spectrum.spectrum_intensity
            #     - df_corrected_spectrum.background_int
            # )

            # multiply by spectrometer df_correction_data.correction factor to get intensity
            # df_corrected_spectrum["intensity"] = (
            #     df_corrected_spectrum["spectrum_m_background"]
            #     * df_basic_data.interpolated
            # )

            # Now do the real calculations
            (
                max_intensity_wavelength,
                cie_color_coordinates,
            ) = ef.calculate_cie_coordinates(
                self.spectrum_data_df.loc[row["device_number"]], df_norm_curves
            )

            self.data_df.at[index, "eqe"] = ef.calculate_eqe(
                self.spectrum_data_df.loc[row["device_number"]],
                self.data_df.loc[index],
                df_basic_data,
                self.measurement_parameters,
            )
            (
                photopic_response,
                self.data_df.at[index, "luminance"],
            ) = ef.calculate_luminance(
                self.spectrum_data_df.loc[row["device_number"]],
                self.data_df.loc[index],
                df_basic_data,
                self.measurement_parameters,
            )

            self.data_df.at[
                index, "luminous_efficiency"
            ] = ef.calculate_luminous_efficacy(
                self.data_df.loc[index], photopic_response, self.measurement_parameters
            )

            self.data_df.at[
                index, "current_efficiency"
            ] = ef.calculate_current_efficiency(
                self.data_df.loc[index], self.measurement_parameters
            )

            self.data_df.at[index, "power_density"] = ef.calculate_power_density(
                self.spectrum_data_df.loc[row["device_number"]],
                row,
                df_basic_data,
                self.measurement_parameters,
            )

            cf.log_message("Data for " + str(index) + " successfully evaluated.")

            # Generate output files
            # generate_output_files(
            #     df_jvl_data,
            #     df_corrected_spectrum,
            #     luminance,
            #     eqe,
            #     luminous_efficiency,
            #     current_efficiency,
            #     power_density,
            #     max_intensity_wavelength,
            #     cie_color_coordinates,
            # )

            # print(file_name + " successfully evaluated and evaluation files saved.")

    # -------------------------------------------------------------------- #
    # ------------------------ Show/plot Groups -------------------------- #
    # -------------------------------------------------------------------- #

    def plot_groups(self):
        """
        Function that allows the plotting of previously assigned groups
        """

        parameters = {
            "device_number": self.assigned_groups_df.index,
            "group_name": self.assigned_groups_df["group_name"].unique(),
        }

        self.show_group_dialog = ShowGroup(parameters, self)
        self.show_group_dialog.show()
        button = self.show_group_dialog.exec_()

    @QtCore.Slot(int)
    def plot_from_device_number(self, device_number):
        """
        Transform device number into a dataframe
        """

        temp_df = self.data_df.loc[self.data_df["device_number"] == device_number]
        self.plot_jvl(temp_df)

    @QtCore.Slot(str)
    def plot_from_group_name(self, group_name):
        """
        Transform group name to df
        """
        temp_df = self.data_df.loc[
            self.data_df.join(self.assigned_groups_df, on="device_number")["group_name"]
            == group_name
        ]
        self.plot_jvl(temp_df)

    def plot_jvl(self, df_to_plot):
        """
        Plot all graphs for a given device number
        """

        if not self.current_plot_type == "jvl":
            # Clear figure and define axis
            self.eval_fig.figure.clf()
            self.eval_ax1 = self.eval_fig.figure.subplots()
            self.eval_ax2 = self.eval_ax1.twinx()
        else:
            self.eval_ax1.cla()
            self.eval_ax2.cla()

        # Change axis to log and add labels
        self.eval_ax1.set_yscale("log")
        self.eval_ax1.set_xlim(
            [min(df_to_plot.iloc[0]["voltage"]), max(df_to_plot.iloc[0]["voltage"])]
        )
        self.eval_ax2.set_yscale("log")
        self.eval_ax1.set_xlabel("Voltage (V)")
        self.eval_ax1.set_ylabel("Current Density (mA cm$^{-2}$)")
        self.eval_ax2.set_ylabel("Luminance (cd m$^{-2}$)")

        # Some more visuals
        self.eval_ax1.set_facecolor("#E0E0E0")
        # self.eval_ax1.tick_params(axis="x", direction="in", length=8)

        # Generate random colors
        cmap = mpl.cm.get_cmap("Dark2", df_to_plot.shape[0])
        device_color = np.array(
            [mpl.colors.rgb2hex(cmap(i)) for i in range(cmap.N)], dtype=object
        )

        self.luminence_lines = []
        self.current_lines = []

        for index in range(df_to_plot.shape[0]):

            self.current_lines.append(
                self.eval_ax1.plot(
                    df_to_plot.iloc[index]["voltage"],
                    df_to_plot.iloc[index]["current_density"],
                    label=df_to_plot.index[index],
                    color=device_color[index],
                )
            )
            self.luminence_lines.append(
                self.eval_ax2.plot(
                    df_to_plot.iloc[index]["voltage"],
                    df_to_plot.iloc[index]["luminance"],
                    linestyle="--",
                    label=df_to_plot.index[index],
                    color=device_color[index],
                )
            )

        # Define legend which shall be draggable and by pressing on elements they hide
        self.current_lines_dict = dict()
        self.luminence_lines_dict = dict()
        self.lineLabel = dict()

        leg = self.eval_ax2.legend(loc="best")
        leg.get_frame().set_alpha(0.4)

        # Make it draggable
        # leg.set_draggable(True)

        # Set the legend's lines thickness
        for legline, curline, lumline, linelabel in zip(
            leg.get_lines(),
            self.current_lines,
            self.luminence_lines,
            self.eval_ax2.get_legend_handles_labels()[1],
        ):
            legline.set_pickradius(5)  # 5 pts tolerance
            legline.set_picker(True)

            self.current_lines_dict[legline] = curline
            self.luminence_lines_dict[legline] = lumline
            self.lineLabel[legline] = linelabel

            # If the line was already masked, mask it on plot
            if self.data_df.loc[self.data_df.index == linelabel, "masked"][0]:
                legline.set_alpha(0.2)
                lumline[0].set_visible(False)
                curline[0].set_visible(False)

        # Connect the pick event to the function onpick()
        self.eval_fig.mpl_connect("pick_event", self.onpick)

        self.eval_fig.figure.tight_layout()
        self.eval_fig.draw()

        self.current_plot_type = "jvl"

    def plot_single_pixel(self, identifier):
        """
        Plot all graphs for a given device number
        """

        temp_df = self.data_df.loc[self.data_df.index == identifier]

        if not self.current_plot_type == "single":
            # Clear figure and define axis
            self.eval_fig.figure.clf()
            self.eval_ax = self.eval_fig.figure.subplots(2, 2)

            # Some more visuals
            self.eval_ax[0, 0].set_facecolor("#E0E0E0")
            self.eval_ax[0, 1].set_facecolor("#E0E0E0")
            self.eval_ax[1, 0].set_facecolor("#E0E0E0")
            self.eval_ax[1, 1].set_facecolor("#E0E0E0")
        else:
            self.eval_ax[0, 0].cla()
            self.eval_ax[0, 1].cla()
            self.eval_ax[1, 0].cla()
            self.eval_ax[1, 1].cla()

        # Plot absolute current density and luminance over voltage
        self.eval_ax5 = self.eval_ax[0, 0].twinx()

        # Change axis to log and add labels
        self.eval_ax[0, 0].set_yscale("log")
        self.eval_ax[0, 0].set_xlim(
            [min(temp_df.iloc[0]["voltage"]), max(temp_df.iloc[0]["voltage"])]
        )
        self.eval_ax5.set_yscale("log")
        self.eval_ax[0, 0].set_xlabel("Voltage (V)")
        self.eval_ax[0, 0].set_ylabel("Current Density (mA cm$^{-2}$)")
        self.eval_ax5.set_ylabel("Luminance (cd m$^{-2}$)")

        self.eval_ax[0, 0].plot(temp_df["voltage"][0], temp_df["current_density"][0])
        self.eval_ax5.plot(
            temp_df["voltage"][0],
            temp_df["luminance"][0],
            linestyle="--",
        )

        # Plot eqe over absolute current density
        self.eval_ax[0, 1].plot(temp_df["current_density"][0], temp_df["eqe"][0])
        self.eval_ax[0, 1].set_xscale("log")
        self.eval_ax[0, 1].set_xlabel("Current Density (mA cm$^{-2}$)")
        self.eval_ax[0, 1].set_ylabel("External Quantum Efficiency (%)")

        # Plot power density over voltage
        self.eval_ax[1, 0].plot(temp_df["voltage"][0], temp_df["power_density"][0])
        self.eval_ax[1, 0].set_yscale("log")
        self.eval_ax[1, 0].set_xlabel("Voltage (V)")
        self.eval_ax[1, 0].set_ylabel("Power Density (mW mm$^{-2}$)")

        # Plot spectrum over wavelength
        spectrum_data = temp_df.join(self.spectrum_data_df, on="device_number")
        self.eval_ax[1, 1].plot(
            spectrum_data["wavelength"][0],
            np.array(spectrum_data["intensity"][0])
            - np.array(spectrum_data["background"][0]),
        )
        self.eval_ax[1, 1].set_xlabel("Wavelength (nm)")
        self.eval_ax[1, 1].set_ylabel("Spectrum (a.u.)")

        # Draw figure
        self.eval_fig.figure.tight_layout()
        self.eval_fig.draw()

        # Set the current plot type for speed enhancement
        self.current_plot_type = "single"

    def onpick(self, event):
        """
        Function that deals with whatever happens when somebody clicks on a
        item in the legend
        """

        # Get the pressed line
        legline = event.artist

        # Now distinguish between left mouse button and mouse wheel press
        if event.mouseevent.button == 1:

            # Translate to the actual graph
            lumline = self.luminence_lines_dict[legline][0]
            curline = self.current_lines_dict[legline][0]

            # Get visibility and set it otherwise
            vis = not lumline.get_visible()
            lumline.set_visible(vis)
            curline.set_visible(vis)

            # Now in the data containing dataframe, set masked as checked (for later stats)
            if not lumline.get_visible():
                legline.set_alpha(0.2)
                self.data_df.loc[self.lineLabel[legline], "masked"] = True
            else:
                legline.set_alpha(1)
                self.data_df.loc[self.lineLabel[legline], "masked"] = False

            # Now redraw diagram
            self.eval_fig.draw()

        elif event.mouseevent.button == 2:
            # On mouse wheel press, plot the four relevant graphs of that pixel
            self.plot_single_pixel(self.lineLabel[legline])

    # -------------------------------------------------------------------- #
    # ------------------------ Show Statistics --------------------------- #
    # -------------------------------------------------------------------- #
    def plot_statistics(self):
        """
        Function that opens dialog to plot statistisc
        """
        self.show_group_dialog = Statistics(self)
        self.show_group_dialog.show()
        button = self.show_group_dialog.exec_()

    def show_statistics(self, groupby):
        """
        Function that calculates the device statistics for all different,
        non-masked pixels and plots them in a
        box plot
        """

        # Unfortunately, a helper dataframe is needed here to extract the
        # statistical parameters. A simple groupby of the data_df does not lead
        # to the right result because one first has to deal with the list
        # inside the lists
        # First get the index of the arrays at 4 V (that is where we do all the
        # stats)
        idx_4v = np.where(np.array(self.data_df["voltage"][0]) == 4.0)[0][0]

        current_density_4v = np.array(
            self.data_df["current_density"]
            .loc[self.data_df["masked"] == False]
            .to_list()
        )[:, idx_4v]
        luminance_4v = np.array(
            self.data_df["luminance"].loc[self.data_df["masked"] == False].to_list()
        )[:, idx_4v]

        device_numbers = (
            self.data_df["device_number"]
            .loc[self.data_df["masked"] == False]
            .to_numpy()
        )
        group_names = (
            self.data_df.loc[self.data_df["masked"] == False]
            .join(self.assigned_groups_df, on="device_number")["group_name"]
            .to_numpy()
        )

        # Now construct a stats dataframe from the above array with which we
        # can easily do the statistics we want
        stats_df = pd.DataFrame(
            np.array(
                [
                    device_numbers.astype(int),
                    group_names,
                    current_density_4v.astype(float),
                    luminance_4v.astype(float),
                ]
            ).T,
            columns=[
                "device_number",
                "group_name",
                "current_density_4v",
                "luminance_4v",
            ],
            index=self.data_df.loc[self.data_df["masked"] == False].index,
        )

        # Convert the dataframe to numeric value and get back the mean of all
        # numeric columns (basically, group_name can not be converted)
        avg_values = stats_df.apply(pd.to_numeric, errors="ignore").groupby(by=groupby)
        current_density_4v_grouped = (
            avg_values["current_density_4v"].apply(list).to_list()
        )

        luminance_4v_grouped = avg_values["luminance_4v"].apply(list).to_list()

        self.boxplot_statistics(
            current_density_4v_grouped,
            luminance_4v_grouped,
            labels=stats_df[groupby].unique(),
        )

    def boxplot_statistics(self, current_density_4v, luminance_4v, labels):
        """
        Does the plotting for the device statistics calculations
        """
        # self._ax[0, 0].boxplot(Voc_dev, labels=labels_, showfliers=False

        if not self.current_plot_type == "boxplot_stats":
            # Clear figure and define axis
            self.eval_fig.figure.clf()
            self.eval_ax = self.eval_fig.figure.subplots(2, 2)

            # Some more visuals
            self.eval_ax[0, 0].set_facecolor("#E0E0E0")
            self.eval_ax[0, 1].set_facecolor("#E0E0E0")
            self.eval_ax[1, 0].set_facecolor("#E0E0E0")
            self.eval_ax[1, 1].set_facecolor("#E0E0E0")
        else:
            self.eval_ax[0, 0].cla()
            self.eval_ax[0, 1].cla()
            self.eval_ax[1, 0].cla()
            self.eval_ax[1, 1].cla()

        # Current at 4 V
        self.eval_ax[0, 0].boxplot(
            current_density_4v, labels=labels.astype(str).tolist(), showfliers=False
        )
        for i in range(len(current_density_4v)):
            temp_y = current_density_4v[i]
            temp_x = np.random.normal(1 + i, 0.04, size=len(temp_y))

            self.eval_ax[0, 0].plot(temp_x, temp_y, "b.")
        self.eval_ax[0, 0].set_ylabel("Current Density (mA cm$^{-2}$)")

        # Luminance at 4 V
        self.eval_ax[0, 1].boxplot(
            luminance_4v, labels=labels.astype(str).tolist(), showfliers=False
        )
        for i in range(len(luminance_4v)):
            temp_y = luminance_4v[i]
            temp_x = np.random.normal(1 + i, 0.04, size=len(temp_y))

            self.eval_ax[0, 1].plot(temp_x, temp_y, "b.")

        self.eval_ax[0, 1].set_ylabel("Luminance (cd m$^{-2}$)")

        self.eval_fig.draw()
        self.current_plot_type = "boxplot_stats"

    # -------------------------------------------------------------------- #
    # ----------------------------- Spectrum ----------------------------- #
    # -------------------------------------------------------------------- #

    def plot_spectrum(self):
        """
        Opens dialog to plot important graphs for each spectrum
        """
        parameters = {
            "device_number": self.assigned_groups_df.index,
            "group_name": self.assigned_groups_df["group_name"].unique(),
        }

        self.show_group_dialog = EvaluateSpectrum(parameters, self)
        self.show_group_dialog.show()
        button = self.show_group_dialog.exec_()

    # -------------------------------------------------------------------- #
    # ---------------------------- Save Data ----------------------------- #
    # -------------------------------------------------------------------- #

    def save_evaluated_data(self):
        """
        Function that saves the evaluated data to files
        """
        print("Save data to files")

    # -------------------------------------------------------------------- #
    # ------------------------- Global Functions ------------------------- #
    # -------------------------------------------------------------------- #

    def show_settings(self):
        """
        Shows the settings
        """
        self.settings_window = Settings(self)
        # ui = Ui_Settings()
        # ui.setupUi(self.settings_window, parent=self)

        p = (
            self.frameGeometry().center()
            - QtCore.QRect(QtCore.QPoint(), self.settings_window.sizeHint()).center()
        )

        self.settings_window.move(p)

        # self.settings_window.show()

        result = self.settings_window.exec()

    def changed_tab_widget(self):
        """
        Function that shall manage the threads that are running when we are
        on a certain tab. For instance the spectrum thread really only must
        run when the user is on the spectrum tab. Otherwise it can be paused.
        This might become important in the future. The best idea is probably
        to just kill all unused threads when we change the tab.
        """

        cf.log_message(
            "Switched to tab widget no. " + str(self.tabWidget.currentIndex())
        )

        return

    def closeEvent(self, event):
        """
        Function that shall allow for save closing of the program
        """

        # Ask the user if he really wants to close if data was not saved yet
        cf.log_message("Program closed")

        # Kill spectrometer thread
        # try:
        #     self.spectrum_measurement.kill()
        # except Exception as e:
        #     cf.log_message("Spectrometer thread could not be killed")
        #     cf.log_message(e)

        # if can_exit:
        event.accept()  # let the window close
        # else:
        #     event.ignore()


# Logging
# Prepare file path etc. for logging
LOG_FILENAME = "./usr/log.out"
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.INFO,
    format=(
        "%(asctime)s - [%(levelname)s] -"
        " (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
    ),
    datefmt="%m/%d/%Y %I:%M:%S %p",
)

# Activate log_rotate to rotate log files after it reached 1 MB size ()
handler = RotatingFileHandler(LOG_FILENAME, maxBytes=1000000)
logging.getLogger("Rotating Log").addHandler(handler)


# ---------------------------------------------------------------------------- #
# -------------------- This is to execute the program ------------------------ #
# ---------------------------------------------------------------------------- #
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = MainWindow()

    # Icon (see https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105#1552105)
    # import ctypes

    # myappid = u"mycompan.myproduct.subproduct.version"  # arbitrary string
    # ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app_icon = QtGui.QIcon()
    app_icon.addFile("./icons/program_icon.png", QtCore.QSize(256, 256))
    app.setWindowIcon(app_icon)

    ui.show()
    sys.exit(app.exec_())
