# -*- coding: utf-8 -*-
from PySide2 import QtCore, QtGui, QtWidgets

import json
import os
import core_functions as cf
from pathlib import Path

from UI_settings_window import Ui_Settings


class Settings(QtWidgets.QDialog, Ui_Settings):
    """
    Settings window
    """

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)

        self.parent = parent

        # Load from file to fill the lines
        settings = cf.read_global_settings()
        self.default_saving_path_lineEdit.setText(settings["default_saving_path"])
        self.photodiode_gain_lineEdit.setText(str(settings["pd_gain"]))
        self.photodiode_area_lineEdit.setText(str(settings["pd_area"]))
        self.read_in_all_scans_toggleSwitch.setChecked(
            bool(settings["include_all_scans"])
        )
        self.distance_photodiode_oled_lineEdit.setText(str(settings["pd_distance"]))
        self.oled_area_lineEdit.setText(str(settings["pixel_area"]))

        self.photopic_response_calibration_path_lineEdit.setText(
            str(settings["photopic_response_path"])
        )
        self.pd_responsivity_calibration_path_lineEdit.setText(
            str(settings["pd_responsivity_path"])
        )
        self.cie_reference_path_lineEdit.setText(str(settings["cie_reference_path"]))
        self.spectrometer_calibration_path_lineEdit.setText(
            str(settings["spectrometer_calibration_path"])
        )
        self.photodiode_gain_path_lineEdit.setText(
            str(settings["photodiode_gain_path"])
        )
        self.read_in_all_scans_toggleSwitch.setChecked(
            bool(settings["include_all_scans"])
        )

        # self.keithley_source_address_lineEdit.setText(
        #     default_settings["keithley_source_address"]
        # )
        # self.keithley_multimeter_address_lineEdit.setText(
        #     default_settings["keithley_multimeter_address"]
        # )

        # Connect buttons to functions
        self.select_default_saving_path_pushButton.clicked.connect(
            self.select_default_saving_path
        )
        self.select_photopic_response_path_pushButton.clicked.connect(
            self.select_photopic_response_path
        )
        self.select_pd_responsivity_calibration_path_pushButton.clicked.connect(
            self.select_pd_responsivity_calibration_path
        )
        self.cie_reference_path_pushButton.clicked.connect(
            self.select_cie_reference_path
        )
        self.spectrometer_calibration_pushButton.clicked.connect(
            self.select_spectrometer_calibration_path
        )
        self.photodiode_gain_path_pushButton.clicked.connect(self.select_pd_gain_path)
        self.load_defaults_pushButton.clicked.connect(self.load_defaults)
        self.save_settings_pushButton.clicked.connect(self.save_settings)

    def save_settings(self):
        """
        Save the settings the user just entered
        """

        # Gather the new settings
        settings_data = {}
        settings_data["overwrite"] = {
            "default_saving_path": self.default_saving_path_lineEdit.text(),
            "include_all_scans": self.read_in_all_scans_toggleSwitch.isChecked(),
            "pd_gain": self.photodiode_gain_lineEdit.text(),
            "pd_area": self.photodiode_area_lineEdit.text(),
            "pd_distance": self.distance_photodiode_oled_lineEdit.text(),
            "pixel_area": self.oled_area_lineEdit.text(),
            "photopic_response_path": self.photopic_response_calibration_path_lineEdit.text(),
            "pd_responsivity_path": self.pd_responsivity_calibration_path_lineEdit.text(),
            "cie_reference_path": self.cie_reference_path_lineEdit.text(),
            "spectrometer_calibration_path": self.spectrometer_calibration_path_lineEdit.text(),
            "photodiode_gain_path": self.photodiode_gain_path_lineEdit.text(),
        }

        # Load the default parameter settings
        # with open(
        #     os.path.join(Path(__file__).parent.parent, "usr", "global_settings.json")
        # ) as json_file:
        #     data = json.load(json_file)
        # #
        # Add the default parameters to the new settings json
        default_data = cf.read_global_settings(default=True)

        settings_data["default"] = []
        settings_data["default"] = default_data

        print(settings_data)
        #
        # Save the entire thing again to the settings.json file
        with open(
            os.path.join(Path(__file__).parent.parent, "usr", "global_settings.json"),
            "w",
        ) as json_file:
            json.dump(settings_data, json_file, indent=4)
        #
        cf.log_message("Settings saved")
        #
        # Close window on accepting
        self.accept()

    def load_defaults(self):
        """
        Load default settings (in case the user messed up the own settings)
        """

        # with open(
        #     os.path.join(Path(__file__).parent.parent, "usr", "global_settings.json")
        # ) as json_file:
        #     data = json.load(json_file)

        # default_settings = data["default"][0]

        default_settings = cf.read_global_settings(default=True)

        self.default_saving_path_lineEdit.setText(
            default_settings["default_saving_path"]
        )
        self.photodiode_gain_lineEdit.setText(str(default_settings["pd_gain"]))
        self.photodiode_area_lineEdit.setText(str(default_settings["pd_area"]))
        self.read_in_all_scans_toggleSwitch.setChecked(
            bool(default_settings["include_all_scans"])
        )
        self.distance_photodiode_oled_lineEdit.setText(
            str(default_settings["pd_distance"])
        )
        self.oled_area_lineEdit.setText(str(default_settings["pixel_area"]))
        self.photopic_response_calibration_path_lineEdit.setText(
            str(default_settings["photopic_response_path"])
        )
        self.pd_responsivity_calibration_path_lineEdit.setText(
            str(default_settings["pd_responsivity_path"])
        )
        self.cie_reference_path_lineEdit.setText(
            str(default_settings["cie_reference_path"])
        )
        self.spectrometer_calibration_path_lineEdit.setText(
            str(default_settings["spectrometer_calibration_path"])
        )
        self.photodiode_gain_path_lineEdit.setText(
            str(default_settings["photodiode_gain_path"])
        )

    def select_default_saving_path(self):
        """
        Function that opens dialog to select default saving path
        """
        path = QtWidgets.QFileDialog.getExistingDirectory(
            QtWidgets.QFileDialog(),
            "Select a Default Saving Path",
            self.default_saving_path_lineEdit.text(),
            QtWidgets.QFileDialog.ShowDirsOnly,
        )
        if path == "":
            return
        else:
            self.default_saving_path_lineEdit.setText(path)

    def select_photopic_response_path(self):
        """
        Function that opens dialog to select default saving path
        """
        path = QtWidgets.QFileDialog.getOpenFileName(
            QtWidgets.QFileDialog(),
            "Select a Photopic Response File",
            self.photopic_response_calibration_path_lineEdit.text(),
        )[0]
        if path == "":
            return
        else:
            self.photopic_response_calibration_path_lineEdit.setText(path)

    def select_pd_responsivity_calibration_path(self):
        """
        Function that opens dialog to select default saving path
        """
        path = QtWidgets.QFileDialog.getOpenFileName(
            QtWidgets.QFileDialog(),
            "Select a PD Responsivity File",
            self.pd_responsivity_calibration_path_lineEdit.text(),
        )[0]
        if path == "":
            return
        else:
            self.pd_responsivity_calibration_path_lineEdit.setText(path)

    def select_cie_reference_path(self):
        """
        Function that opens dialog to select default saving path
        """
        path = QtWidgets.QFileDialog.getOpenFileName(
            QtWidgets.QFileDialog(),
            "Select a CIE Reference File",
            self.cie_reference_path_lineEdit.text(),
        )[0]
        if path == "":
            return
        else:
            self.cie_reference_path_lineEdit.setText(path)

    def select_spectrometer_calibration_path(self):
        """
        Function that opens dialog to select default saving path
        """
        path = QtWidgets.QFileDialog.getOpenFileName(
            QtWidgets.QFileDialog(),
            "Select a Spectrometer Calibration File",
            self.spectrometer_calibration_path_lineEdit.text(),
        )[0]
        if path == "":
            return
        else:
            self.spectrometer_calibration_path_lineEdit.setText(path)

    def select_pd_gain_path(self):
        """
        Function that opens dialog to select default saving path
        """
        path = QtWidgets.QFileDialog.getOpenFileName(
            QtWidgets.QFileDialog(),
            "Select a PD Gain File",
            self.photodiode_gain_path_lineEdit.text(),
        )[0]
        if path == "":
            return
        else:
            self.photodiode_gain_path_lineEdit.setText(path)