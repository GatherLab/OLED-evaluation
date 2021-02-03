from UI_main_window import Ui_MainWindow
from settings import Settings
from assign_groups import AssignGroups

# from loading_window import LoadingWindow

# from spectrum_measurement import SpectrumMeasurement

# from hardware import RigolOscilloscope, VoltcraftSource

import core_functions as cf

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
            columns=["group_name", "device_numbers", "spectrum_path", "colors"]
        )

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
        self.eval_save_pushButton.clicked.connect(self.save_evaluated_data)

        # Set all buttons except for the change path pushButton to disable
        # until a folder was selected
        # self.eval_assign_groups_pushButton.setEnabled(False)
        # self.eval_plot_groups_pushButton.setEnabled(False)
        # self.eval_save_pushButton.setEnabled(False)

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
    # ------------------------- Global Functions ------------------------- #
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
        device_numbers = []
        pixel_numbers = []
        scan_number = []
        identifier = []

        for name in file_names:
            split_name = name.split("_")
            if len(split_name) == 4:
                # Right file name but only one scan
                dates.append(str(split_name[0]))
                batch_names.append(str(split_name[1]))
                device_numbers.append(int(split_name[2][1:]))
                pixel_numbers.append(int(split_name[3].split(".")[0][1:]))
                scan_number.append(1)
                identifier.append(split_name[2] + split_name[3].split(".")[0])
            elif len(split_name) == 5:
                # If this is > first scan
                dates.append(str(split_name[0]))
                batch_names.append(str(split_name[1]))
                device_numbers.append(int(split_name[2][1:]))
                pixel_numbers.append(int(split_name[3][1:]))
                identifier.append(split_name[2] + split_name[3])
                scan_number.append(int(split_name[4].split(".")[0][1:]))
            else:
                # File name is not in the correct format
                cf.log_message(
                    "The file name does not follow the naming convention date_batch-name_d<no>_p<no>_<no>.csv"
                )
        if np.size(np.unique(batch_names)) > 1:
            cf.log_message(
                "The batch name does not match for all files. If there are different OLEDs with the same device number this could lead to a problem."
            )

        self.files_df["file_name"] = file_names
        self.files_df["device"] = device_numbers
        self.files_df["pixel_numbers"] = pixel_numbers
        self.files_df["scan_number"] = scan_number
        self.files_df["identifier"] = identifier

        # return the maximum scan number in the investigated batch
        self.max_scan_number = np.max(scan_number)

        # Now generate a dictionary containing the device numbers as keys and
        # an array of the pixel numbers as values
        # self.devices_and_pixels = {}

        # for i in np.unique(device_numbers):
        #     self.devices_and_pixels[i] = np.array(pixel_numbers)[
        #         np.where(np.array(device_numbers, dtype=int) == i)[0]
        #     ]

    def assign_groups(self):
        """
        Function that opens the assign group dialog and allows to assign groups
        """
        parameters = {
            "no_of_scans": self.max_scan_number,
            "device_numbers": np.unique(self.files_df["device"].to_list()),
            "assigned_groups_df": self.assigned_groups_df,
        }

        self.assign_groups_dialog = AssignGroups(parameters, self)
        self.assign_groups_dialog.show()
        button = self.assign_groups_dialog.exec_()

        # Now check if user pressed close or save
        if button == True:
            # Only select those files that's device numbers were entered by the user
            selected_files = self.files_df[
                self.files_df["device"].isin(
                    np.concatenate(self.assigned_groups_df["device_numbers"].to_numpy())
                )
            ]
            # Now read in the files for selected devices
            self.data_df = cf.read_files(
                [
                    self.global_path + "/" + file_name
                    for file_name in selected_files["file_name"]
                ],
                ["voltage", "current", "pd_voltage"],
                selected_files["identifier"],
                " ",
                skip_row=10,
            )
            self.groups_assigned = True
            self.eval_plot_groups_pushButton.setEnabled(True)
            self.eval_save_pushButton.setEnabled(True)
        else:
            cf.log_message("Group assignement aborted")

    def plot_groups(self):
        """
        Function that allows the plotting of previously assigned groups
        """
        print("Plot groups")

    def save_evaluated_data(self):
        """
        Function that saves the evaluated data to files
        """
        print("Save data to files")

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

    # def open_file(self, path):
    #     """
    #     Opens a file on the machine with the standard program
    #     https://stackoverflow.com/questions/6045679/open-file-with-pyqt
    #     """
    #     if sys.platform.startswith("linux"):
    #         subprocess.call(["xdg-open", path])
    #     else:
    #         os.startfile(path)

    # @QtCore.Slot(str)
    # def cf.log_message(self, message):
    #     """
    #     Function that manages the logging, in the sense that everything is
    #     directly logged into statusbar and the log file at once as well as
    #     printed to the console instead of having to call multiple functions.
    #     """
    #     self.statusbar.showMessage(message, 10000000)
    #     logging.info(message)
    #     print(message)

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

    @QtCore.Slot(list, list)
    def update_spectrum(self, wavelength, intensity):
        """
        Function that is continuously evoked when the spectrum is updated by
        the other thread
        """
        # Clear plot
        # self.eval_ax.cla()
        del self.eval_ax.lines[0]

        # Plot current
        self.eval_ax.plot(
            wavelength,
            intensity,
            color=(68 / 255, 188 / 255, 65 / 255),
            marker="o",
        )

        self.eval_fig.draw()

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
