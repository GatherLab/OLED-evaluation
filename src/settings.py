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
        # default_settings = cf.read_global_settings()

        # self.keithley_source_address_lineEdit.setText(
        #     default_settings["keithley_source_address"]
        # )
        # self.keithley_multimeter_address_lineEdit.setText(
        #     default_settings["keithley_multimeter_address"]
        # )

        # Connect buttons to functions
        self.load_defaults_pushButton.clicked.connect(self.load_defaults)
        self.save_settings_pushButton.clicked.connect(self.save_settings)

    def save_settings(self):
        """
        Save the settings the user just entered
        """

        # # Gather the new settings
        # settings_data = {}
        # settings_data["overwrite"] = []
        # settings_data["overwrite"].append(
        #     {
        #         "keithley_source_address": self.keithley_source_address_lineEdit.text(),
        #         "keithley_multimeter_address": self.keithley_multimeter_address_lineEdit.text(),
        #         "arduino_com_address": self.arduino_com_address_lineEdit.text(),
        #         "motor_number": self.motor_number_lineEdit.text(),
        #         "motor_offset": self.motor_offset_lineEdit.text(),
        #         "spectrum_integration_time": self.spectrum_integration_time_lineEdit.text(),
        #         "photodiode_cutoff": self.photodiode_cutoff_lineEdit.text(),
        #         "photodiode_saturation": self.photodiode_saturation_lineEdit.text(),
        #         "photodiode_area": self.photodiode_area_lineEdit.text(),
        #         "photodiode_peak_response": self.photodiode_peak_response_lineEdit.text(),
        #         "amplifier_resistance": self.amplifier_resistance_lineEdit.text(),
        #         "oled_area": self.oled_area_lineEdit.text(),
        #         "distance_photodiode_oled": self.distance_photodiode_oled_lineEdit.text(),
        #         "default_saving_path": self.default_saving_path_lineEdit.text(),
        #     }
        # )

        # # Load the default parameter settings
        # with open(
        #     os.path.join(Path(__file__).parent.parent, "usr", "global_settings.json")
        # ) as json_file:
        #     data = json.load(json_file)

        # # Add the default parameters to the new settings json
        # settings_data["default"] = []
        # settings_data["default"] = data["default"]
        # print(settings_data)

        # # Save the entire thing again to the settings.json file
        # with open(
        #     os.path.join(Path(__file__).parent.parent, "usr", "global_settings.json"),
        #     "w",
        # ) as json_file:
        #     json.dump(settings_data, json_file, indent=4)

        # cf.log_message("Settings saved")

        # # Close window on accepting
        # self.accept()

        # # Before closing the window, reinstanciate the devices with the new
        # # parameters
        # loading_window = LoadingWindow(self.parent)

        # # Execute loading dialog
        # loading_window.exec()
        print("Test")

    def load_defaults(self):
        """
        Load default settings (in case the user messed up the own settings)
        """

        print("Test")
        # with open(
        #     os.path.join(Path(__file__).parent.parent, "usr", "global_settings.json")
        # ) as json_file:
        #     data = json.load(json_file)

        # default_settings = data["default"][0]
        # self.keithley_source_address_lineEdit.setText(
        #     default_settings["keithley_source_address"]
        # )
        # self.keithley_multimeter_address_lineEdit.setText(
        #     default_settings["keithley_multimeter_address"]
        # )
        # self.arduino_com_address_lineEdit.setText(
        #     default_settings["arduino_com_address"]
        # )
        # self.motor_number_lineEdit.setText(default_settings["motor_number"])
        # self.motor_offset_lineEdit.setText(default_settings["motor_offset"])
        # self.spectrum_integration_time_lineEdit.setText(
        #     default_settings["spectrum_integration_time"]
        # )
        # self.photodiode_cutoff_lineEdit.setText(default_settings["photodiode_cutoff"])
        # self.photodiode_saturation_lineEdit.setText(
        #     default_settings["photodiode_saturation"]
        # )
        # self.photodiode_area_lineEdit.setText(default_settings["photodiode_area"])
        # self.photodiode_peak_response_lineEdit.setText(
        #     default_settings["photodiode_peak_response"]
        # )
        # self.amplifier_resistance_lineEdit.setText(
        #     default_settings["amplifier_resistance"]
        # )
        # self.oled_area_lineEdit.setText(default_settings["oled_area"])
        # self.distance_photodiode_oled_lineEdit.setText(
        #     default_settings["distance_photodiode_oled"]
        # )
        # self.default_saving_path_lineEdit.setText(
        #     default_settings["default_saving_path"]
        # )
