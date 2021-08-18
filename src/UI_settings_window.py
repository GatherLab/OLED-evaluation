# -*- coding: utf-8 -*-
from PySide2 import QtCore, QtGui, QtWidgets

import json
import core_functions as cf


class Ui_Settings(object):
    def setupUi(self, Settings, parent=None):
        # Note: this is not how it should be done but currently I don't know
        # how to do it differently. This is only needed to be able to emit
        # signals to the main window
        self.parent = parent

        Settings.setObjectName("Settings")
        Settings.resize(800, 400)
        Settings.setStyleSheet(
            "QWidget {\n"
            "            background-color: rgb(44, 49, 60);\n"
            "            color: rgb(255, 255, 255);\n"
            '            font: 63 10pt "Segoe UI";\n'
            "}\n"
            "QPushButton {\n"
            "            border: 2px solid rgb(52, 59, 72);\n"
            "            border-radius: 5px;\n"
            "            background-color: rgb(52, 59, 72);\n"
            "}\n"
            "QPushButton:hover {\n"
            "            background-color: rgb(57, 65, 80);\n"
            "            border: 2px solid rgb(61, 70, 86);\n"
            "}\n"
            "QPushButton:pressed {\n"
            "            background-color: rgb(35, 40, 49);\n"
            "            border: 2px solid rgb(43, 50, 61);\n"
            "}\n"
            "QPushButton:checked {\n"
            "            background-color: rgb(35, 40, 49);\n"
            "            border: 2px solid rgb(85, 170, 255);\n"
            "}"
            "QLineEdit {\n"
            "            border: 2px solid rgb(61, 70, 86);\n"
            "            border-radius: 5px;\n"
            "            background-color: rgb(52, 59, 72);\n"
            "}\n"
            "QSpinBox {\n"
            "            border: 2px solid rgb(61, 70, 86);\n"
            "            border-radius: 5px;\n"
            "            background-color: rgb(52, 59, 72);\n"
            "}\n"
            "QDoubleSpinBox {\n"
            "            border: 2px solid rgb(61, 70, 86);\n"
            "            border-radius: 5px;\n"
            "            background-color: rgb(52, 59, 72);\n"
            "}\n"
        )
        self.gridLayout = QtWidgets.QGridLayout(Settings)
        self.gridLayout.setContentsMargins(25, 10, 25, 10)
        self.gridLayout.setObjectName("gridLayout")

        # Global Software Settings
        self.global_settings_header_label = QtWidgets.QLabel(Settings)
        self.global_settings_header_label.setMinimumSize(QtCore.QSize(0, 20))
        self.global_settings_header_label.setStyleSheet(
            'font: 75 bold 10pt "Segoe UI";'
        )
        self.global_settings_header_label.setObjectName("global_settings_header_label")
        self.gridLayout.addWidget(self.global_settings_header_label, 0, 0, 1, 2)

        self.header_line_3 = QtWidgets.QFrame()
        self.header_line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.header_line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.gridLayout.addWidget(self.header_line_3, 1, 0, 1, 2)
        self.header_line_3.setStyleSheet(
            "QFrame {\n" "            border: 2px solid rgb(52, 59, 72);\n" "}\n"
        )

        # Standard Saving Path
        self.default_saving_path_label = QtWidgets.QLabel(Settings)
        self.default_saving_path_label.setObjectName("default_saving_path_label")
        self.gridLayout.addWidget(self.default_saving_path_label, 2, 0, 1, 1)

        self.default_saving_path_HLayout = QtWidgets.QHBoxLayout()
        self.select_default_saving_path_pushButton = QtWidgets.QPushButton(Settings)
        self.select_default_saving_path_pushButton.setObjectName(
            "select_default_saving_path_pushButton"
        )

        self.default_saving_path_lineEdit = QtWidgets.QLineEdit(Settings)
        self.default_saving_path_lineEdit.setObjectName("default_saving_path_lineEdit")
        self.default_saving_path_HLayout.addWidget(self.default_saving_path_lineEdit)
        self.default_saving_path_HLayout.addWidget(
            self.select_default_saving_path_pushButton
        )
        self.gridLayout.addLayout(self.default_saving_path_HLayout, 2, 1, 1, 1)

        # Data Evaluation Settings
        self.data_evaluation_header_label = QtWidgets.QLabel(Settings)
        self.data_evaluation_header_label.setMinimumSize(QtCore.QSize(0, 20))
        self.data_evaluation_header_label.setStyleSheet(
            'font: 75 bold 10pt "Segoe UI";'
        )
        self.data_evaluation_header_label.setObjectName("data_evaluation_header_label")
        self.gridLayout.addWidget(self.data_evaluation_header_label, 3, 0, 1, 2)

        self.header_line_2 = QtWidgets.QFrame()
        self.header_line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.header_line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.gridLayout.addWidget(self.header_line_2, 4, 0, 1, 2)
        self.header_line_2.setStyleSheet(
            "QFrame {\n" "            border: 2px solid rgb(52, 59, 72);\n" "}\n"
        )

        # Photodiode gain
        self.photodiode_gain_label = QtWidgets.QLabel(Settings)
        self.photodiode_gain_label.setObjectName("photodiode_gain_label")
        self.gridLayout.addWidget(self.photodiode_gain_label, 5, 0, 1, 1)
        self.photodiode_gain_lineEdit = QtWidgets.QLineEdit(Settings)
        self.photodiode_gain_lineEdit.setObjectName("photodiode_gain_lineEdit")
        self.gridLayout.addWidget(self.photodiode_gain_lineEdit, 5, 1, 1, 1)

        # Photodiode area
        self.photodiode_area_label = QtWidgets.QLabel(Settings)
        self.photodiode_area_label.setObjectName("photodiode_area_label")
        self.gridLayout.addWidget(self.photodiode_area_label, 6, 0, 1, 1)
        self.photodiode_area_lineEdit = QtWidgets.QLineEdit(Settings)
        self.photodiode_area_lineEdit.setObjectName("photodiode_area_lineEdit")
        self.gridLayout.addWidget(self.photodiode_area_lineEdit, 6, 1, 1, 1)

        # Distance photodiode, OLED
        self.distance_photodiode_oled_label = QtWidgets.QLabel(Settings)
        self.distance_photodiode_oled_label.setObjectName(
            "distance_photodiode_oled_label"
        )
        self.gridLayout.addWidget(self.distance_photodiode_oled_label, 7, 0, 1, 1)
        self.distance_photodiode_oled_lineEdit = QtWidgets.QLineEdit(Settings)
        self.distance_photodiode_oled_lineEdit.setObjectName(
            "distance_photodiode_oled_lineEdit"
        )
        self.gridLayout.addWidget(self.distance_photodiode_oled_lineEdit, 7, 1, 1, 1)

        # Active OLED area
        self.oled_area_label = QtWidgets.QLabel(Settings)
        self.oled_area_label.setObjectName("oled_area_label")
        self.gridLayout.addWidget(self.oled_area_label, 8, 0, 1, 1)
        self.oled_area_lineEdit = QtWidgets.QLineEdit(Settings)
        self.oled_area_lineEdit.setObjectName("oled_area_lineEdit")
        self.gridLayout.addWidget(self.oled_area_lineEdit, 8, 1, 1, 1)

        # Calibration File Paths
        self.calibration_file_path_header_label = QtWidgets.QLabel(Settings)
        self.calibration_file_path_header_label.setMinimumSize(QtCore.QSize(0, 20))
        self.calibration_file_path_header_label.setStyleSheet(
            'font: 75 bold 10pt "Segoe UI";'
        )
        self.calibration_file_path_header_label.setObjectName(
            "calibration_file_path_header_label"
        )
        self.gridLayout.addWidget(self.calibration_file_path_header_label, 9, 0, 1, 2)

        self.header_line_4 = QtWidgets.QFrame()
        self.header_line_4.setFrameShape(QtWidgets.QFrame.HLine)
        self.header_line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.gridLayout.addWidget(self.header_line_3, 10, 0, 1, 2)
        self.header_line_4.setStyleSheet(
            "QFrame {\n" "            border: 2px solid rgb(52, 59, 72);\n" "}\n"
        )

        # Photopic response path
        self.photopic_response_calibration_path_label = QtWidgets.QLabel(Settings)
        self.photopic_response_calibration_path_label.setObjectName(
            "photopic_response_calibration_path_label"
        )
        self.gridLayout.addWidget(
            self.photopic_response_calibration_path_label, 11, 0, 1, 1
        )

        self.photopic_response_path_HLayout = QtWidgets.QHBoxLayout()
        self.select_photopic_response_path_pushButton = QtWidgets.QPushButton(Settings)
        self.select_photopic_response_path_pushButton.setObjectName(
            "select_photopic_response_path_pushButton"
        )

        self.photopic_response_calibration_path_lineEdit = QtWidgets.QLineEdit(Settings)
        self.photopic_response_calibration_path_lineEdit.setObjectName(
            "photopic_response_calibration_path_lineEdit"
        )
        self.photopic_response_path_HLayout.addWidget(
            self.photopic_response_calibration_path_lineEdit
        )
        self.photopic_response_path_HLayout.addWidget(
            self.select_photopic_response_path_pushButton
        )
        self.gridLayout.addLayout(self.photopic_response_path_HLayout, 11, 1, 1, 1)

        # PD responsivity path
        self.pd_responsivity_calibration_path_label = QtWidgets.QLabel(Settings)
        self.pd_responsivity_calibration_path_label.setObjectName(
            "pd_responsivity_calibration_path_label"
        )
        self.gridLayout.addWidget(
            self.pd_responsivity_calibration_path_label, 12, 0, 1, 1
        )

        self.pd_responsivity_calibration_path_HLayout = QtWidgets.QHBoxLayout()
        self.select_pd_responsivity_calibration_path_pushButton = QtWidgets.QPushButton(
            Settings
        )
        self.select_pd_responsivity_calibration_path_pushButton.setObjectName(
            "select_pd_responsivity_calibration_path_pushButton"
        )
        self.pd_responsivity_calibration_path_lineEdit = QtWidgets.QLineEdit(Settings)
        self.pd_responsivity_calibration_path_lineEdit.setObjectName(
            "pd_responsivity_calibration_path_lineEdit"
        )

        self.pd_responsivity_calibration_path_HLayout.addWidget(
            self.pd_responsivity_calibration_path_lineEdit
        )
        self.pd_responsivity_calibration_path_HLayout.addWidget(
            self.select_pd_responsivity_calibration_path_pushButton
        )
        self.gridLayout.addLayout(
            self.pd_responsivity_calibration_path_HLayout, 12, 1, 1, 1
        )

        # CIE reference path
        self.cie_reference_path_label = QtWidgets.QLabel(Settings)
        self.cie_reference_path_label.setObjectName("cie_reference_path_label")
        self.gridLayout.addWidget(self.cie_reference_path_label, 13, 0, 1, 1)

        self.cie_reference_path_HLayout = QtWidgets.QHBoxLayout()
        self.cie_reference_path_pushButton = QtWidgets.QPushButton(Settings)
        self.cie_reference_path_pushButton.setObjectName(
            "cie_reference_path_pushButton"
        )

        self.cie_reference_path_lineEdit = QtWidgets.QLineEdit(Settings)
        self.cie_reference_path_lineEdit.setObjectName("cie_reference_path_lineEdit")

        self.cie_reference_path_HLayout.addWidget(self.cie_reference_path_lineEdit)
        self.cie_reference_path_HLayout.addWidget(self.cie_reference_path_pushButton)
        self.gridLayout.addLayout(self.cie_reference_path_HLayout, 13, 1, 1, 1)

        # Spectrometer Calibration path
        self.spectrometer_calibration_path_label = QtWidgets.QLabel(Settings)
        self.spectrometer_calibration_path_label.setObjectName(
            "spectrometer_calibration_path_label"
        )
        self.gridLayout.addWidget(self.spectrometer_calibration_path_label, 14, 0, 1, 1)

        self.spectrometer_calibration_HLayout = QtWidgets.QHBoxLayout()
        self.spectrometer_calibration_pushButton = QtWidgets.QPushButton(Settings)
        self.spectrometer_calibration_pushButton.setObjectName(
            "spectrometer_calibration_pushButton"
        )

        self.spectrometer_calibration_path_lineEdit = QtWidgets.QLineEdit(Settings)
        self.spectrometer_calibration_path_lineEdit.setObjectName(
            "spectrometer_calibration_path_lineEdit"
        )

        self.spectrometer_calibration_HLayout.addWidget(
            self.spectrometer_calibration_path_lineEdit
        )
        self.spectrometer_calibration_HLayout.addWidget(
            self.spectrometer_calibration_pushButton
        )
        self.gridLayout.addLayout(self.spectrometer_calibration_HLayout, 14, 1, 1, 1)

        # Photodiode gain path
        self.photodiode_gain_path_label = QtWidgets.QLabel(Settings)
        self.photodiode_gain_path_label.setObjectName("photodiode_gain_path_label")
        self.gridLayout.addWidget(self.photodiode_gain_path_label, 15, 0, 1, 1)

        self.photodiode_gain_path_HLayout = QtWidgets.QHBoxLayout()
        self.photodiode_gain_path_pushButton = QtWidgets.QPushButton(Settings)
        self.photodiode_gain_path_pushButton.setObjectName(
            "photodiode_gain_path_pushButton"
        )

        self.photodiode_gain_path_lineEdit = QtWidgets.QLineEdit(Settings)
        self.photodiode_gain_path_lineEdit.setObjectName(
            "photodiode_gain_path_lineEdit"
        )

        self.photodiode_gain_path_HLayout.addWidget(self.photodiode_gain_path_lineEdit)
        self.photodiode_gain_path_HLayout.addWidget(
            self.photodiode_gain_path_pushButton
        )
        self.gridLayout.addLayout(self.photodiode_gain_path_HLayout, 15, 1, 1, 1)

        # Push Buttons
        self.buttons_HBoxLayout = QtWidgets.QHBoxLayout()
        self.load_defaults_pushButton = QtWidgets.QPushButton(Settings)
        self.load_defaults_pushButton.setObjectName("load_defaults_pushButton")
        self.buttons_HBoxLayout.addWidget(self.load_defaults_pushButton)

        self.save_settings_pushButton = QtWidgets.QPushButton(Settings)
        self.save_settings_pushButton.setObjectName("save_settings_pushButton")
        self.buttons_HBoxLayout.addWidget(self.save_settings_pushButton)

        self.gridLayout.addLayout(self.buttons_HBoxLayout, 16, 0, 1, 2)

        self.retranslateUi(Settings)
        QtCore.QMetaObject.connectSlotsByName(Settings)

    def retranslateUi(self, Settings):
        _translate = QtCore.QCoreApplication.translate
        Settings.setWindowTitle(_translate("Settings", "Options"))
        self.global_settings_header_label.setText(
            _translate("Settings", "Software Settings")
        )
        self.calibration_file_path_header_label.setText(
            _translate("Settings", "Calibration File Paths")
        )

        self.default_saving_path_label.setText(_translate("Settings", "Default Path"))
        self.select_default_saving_path_pushButton.setText(
            _translate("Settings", " Select ")
        )
        self.select_pd_responsivity_calibration_path_pushButton.setText(
            _translate("Settings", " Select ")
        )
        self.select_photopic_response_path_pushButton.setText(
            _translate("Settings", " Select ")
        )
        self.cie_reference_path_pushButton.setText(_translate("Settings", " Select "))
        self.spectrometer_calibration_pushButton.setText(
            _translate("Settings", " Select ")
        )
        self.photodiode_gain_path_pushButton.setText(_translate("Settings", " Select "))

        self.data_evaluation_header_label.setText(
            _translate("Settings", "Settings for Data Evaluation")
        )
        self.photodiode_gain_label.setText(
            _translate("Settings", "Photodiode Gain (dB)")
        )
        self.photodiode_area_label.setText(
            _translate("Settings", "Photodiode Area (mm^2)")
        )

        self.oled_area_label.setText(_translate("Settings", "Active OLED Area (mm^2)"))
        self.distance_photodiode_oled_label.setText(
            _translate("Settings", "Distance Photodiode-OLED (mm)")
        )
        self.photopic_response_calibration_path_label.setText(
            _translate("Settings", "Photopic Response Calibration File Path")
        )
        self.pd_responsivity_calibration_path_label.setText(
            _translate("Settings", "PD Responsivity Calibration File Path")
        )
        self.cie_reference_path_label.setText(
            _translate("Settings", "CIE Reference Calibration File Path")
        )
        self.spectrometer_calibration_path_label.setText(
            _translate("Settings", "Spectrometer Calibration File Path")
        )

        self.photodiode_gain_path_label.setText(
            _translate("Settings", "Photodiode Gain Conversion File Path")
        )

        self.save_settings_pushButton.setText(_translate("Settings", "Save Settings"))
        self.load_defaults_pushButton.setText(_translate("Settings", "Load Defaults"))
