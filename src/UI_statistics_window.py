# -*- coding: utf-8 -*-
from PySide2 import QtCore, QtGui, QtWidgets

import json
import core_functions as cf
import numpy as np


class Ui_Statistics(object):
    def setupUi(self, Statistics):
        # Note: this is not how it should be done but currently I don't know
        # how to do it differently. This is only needed to be able to emit
        # signals to the main window

        Statistics.setObjectName("Statistics")
        Statistics.setWindowTitle("Show Statistics")
        Statistics.resize(400, 100)
        Statistics.setStyleSheet(
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
        self.verticalLayout = QtWidgets.QVBoxLayout(Statistics)
        self.verticalLayout.setContentsMargins(25, 10, 25, 10)
        self.verticalLayout.setObjectName("verticalLayout")

        # Define dialog in which parameters should be entered
        # dialog = QtWidgets.QDialog()
        # dialog.setWindowTitle("Show Group Dialog")

        # Define all the layouts and labels so that the window looks good
        # verticalLayout = QtWidgets.QVBoxLayout()
        self.header_label = QtWidgets.QLabel()
        self.header_label.setObjectName("header_label")
        self.verticalLayout.addWidget(self.header_label)

        # In a grid layout put buttons for all the valid devices
        self.horizontalLayout = QtWidgets.QHBoxLayout()

        self.statistics_by_group_pushButton = QtWidgets.QPushButton("Group")
        self.statistics_by_device_pushButton = QtWidgets.QPushButton("Device")
        # self.statistics_by_group_pushButtonAvg = QtWidgets.QPushButton("Avg Group")

        # self.statistics_by_group_pushButtonAvg.clicked.connect(
        # functools.partial(self.showOverview, "groups", "forward", avg=True)
        # )

        # if self.groupsAssigned == True:
        # self.statistics_by_group_pushButton.setEnabled(True)
        # self.statistics_by_group_pushButtonAvg.setEnabled(True)
        # elif self.groupsAssigned == False:
        # self.statistics_by_group_pushButton.setEnabled(False)
        # self.statistics_by_group_pushButtonAvg.setEnabled(False)

        self.horizontalLayout.addWidget(self.statistics_by_device_pushButton)
        self.horizontalLayout.addWidget(self.statistics_by_group_pushButton)
        # self.horizontalLayout.addWidget(self.statistics_by_group_pushButtonAvg)

        self.verticalLayout.addLayout(self.horizontalLayout)

        # If there is dual data it must be possible to plot it seperately
        # if self.isDual == True:
        # verticalLayout.addWidget(QtWidgets.QLabel("Show Overview of Reverse Data:"))
        # self.horizontalLayoutRev = QtWidgets.QHBoxLayout()
        #
        # if self.multipleFoldersLoaded == False:
        # self.buttonOverviewDevicesRev = QtWidgets.QPushButton("Devices")
        # self.buttonOverviewDevicesRev.clicked.connect(
        # functools.partial(self.showOverview, "devices", "reverse")
        # )
        # self.horizontalLayoutRev.addWidget(self.buttonOverviewDevicesRev)
        #
        # self.statistics_by_group_pushButtonRev = QtWidgets.QPushButton("Group")
        # self.statistics_by_group_pushButtonRevAvg = QtWidgets.QPushButton(
        # "Avg Group"
        # )
        # self.statistics_by_group_pushButtonRev.clicked.connect(
        # functools.partial(self.showOverview, "groups", "reverse")
        # )
        # self.statistics_by_group_pushButtonRevAvg.clicked.connect(
        # functools.partial(self.showOverview, "groups", "reverse", avg=True)
        # )
        #
        # self.horizontalLayoutRev.addWidget(self.statistics_by_group_pushButtonRev)
        # self.horizontalLayoutRev.addWidget(
        # self.statistics_by_group_pushButtonRevAvg
        # )
        # verticalLayout.addLayout(self.horizontalLayoutRev)
        #
        # if self.groupsAssigned == True:
        # self.statistics_by_group_pushButtonRev.setEnabled(True)
        # elif self.groupsAssigned == False:
        # self.statistics_by_group_pushButtonRev.setEnabled(False)

        # Add an exit button to the dialog
        self.close_pushButton = QtWidgets.QPushButton("Close")

        self.verticalLayout.addWidget(self.close_pushButton)

        self.setLayout(self.verticalLayout)

        self.retranslateUi(Statistics)
        QtCore.QMetaObject.connectSlotsByName(Statistics)

    def retranslateUi(self, Statistics):
        _translate = QtCore.QCoreApplication.translate
        Statistics.setWindowTitle(_translate("Statistics", "Show Statistics"))

        self.header_label.setText(_translate("Statistics", "Show Statistics"))
