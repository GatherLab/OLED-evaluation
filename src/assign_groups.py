# -*- coding: utf-8 -*-
from PySide2 import QtCore, QtGui, QtWidgets

import json
import os
import core_functions as cf
from pathlib import Path
import functools

import numpy as np
import pandas as pd

import randomcolor

from UI_assign_group import Ui_AssignGroup


class AssignGroups(QtWidgets.QDialog, Ui_AssignGroup):
    """
    Settings window
    """

    def __init__(self, parameters, parent=None):
        QtWidgets.QDialog.__init__(self)
        self.parent = parent
        self.parameters = parameters
        rand_color = randomcolor.RandomColor()

        self.group_color = np.array(
            rand_color.generate(
                hue="blue", count=np.size(parameters["device_numbers"])
            ),
            dtype=object,
        )
        self.group_spectrum_path = np.empty(
            np.size(parameters["device_numbers"]), dtype=object
        )

        # The manual group count is needed to keep track of the number of
        # groups being assigned
        self.manual_group_count = 1

        self.setupUi(self)

        # Connect functions to buttons
        self.no_groups_LabeledSlider.valueChanged(self.no_groups_slider_changed)
        self.group_spectrum_PushButton_container[0].clicked.connect(
            functools.partial(self.change_spectrum, 0)
        )
        self.group_colors_PushButton_container[0].clicked.connect(
            functools.partial(self.change_group_color, 0)
        )
        self.close_pushButton.clicked.connect(self.close_without_saving)
        self.save_pushButton.clicked.connect(self.save_groups)

        # In case groups were already assigned the dialog should be directly
        # initalised with those groups
        no_groups = self.parameters["assigned_groups_df"]["group_name"].size
        if no_groups > 0:

            self.no_groups_LabeledSlider.setValue(no_groups)
            self.no_groups_slider_changed()

            for group_number in range(no_groups):
                self.group_name_LineEdit_container[group_number].setText(
                    self.parameters["assigned_groups_df"]["group_name"].astype("U13")[
                        group_number
                    ]
                )

                self.device_assignment_LineEdit_container[group_number].setText(
                    ",".join(
                        map(
                            str,
                            self.parameters["assigned_groups_df"][
                                "device_numbers"
                            ].to_numpy()[group_number],
                        )
                    )
                )
                self.group_spectrum_path[group_number] = self.parameters[
                    "assigned_groups_df"
                ]["spectrum_path"][group_number]
                self.group_color[group_number] = self.parameters["assigned_groups_df"][
                    "colors"
                ][group_number]
                try:
                    if os.path.isfile(self.group_spectrum_path[group_number]):
                        self.group_spectrum_PushButton_container[
                            group_number
                        ].setStyleSheet("background-color: green")
                except:
                    cf.log_message(
                        "Spectrum file for group "
                        + str(
                            self.parameters["assigned_groups_df"]["group_name"][
                                group_number
                            ]
                        )
                        + " could not be loaded. Please set again."
                    )

                self.group_colors_PushButton_container[group_number].setStyleSheet(
                    "background-color: " + str(self.group_color[group_number])
                )

    def no_groups_slider_changed(self):
        """
        Function that changes the UI if the slider that manages the number of groups changed
        """

        # If the slider in assignGroup_dialog is moved the window has to be
        # updated according to the number of groups that shall be named.

        # Read out the Slider value
        no_groups = self.no_groups_LabeledSlider.value()

        # Compare if the slider value is greater or smaller than the shown no
        # of QLineEdits. Add or delete elements accordingly.
        if self.manual_group_count < no_groups:
            while self.manual_group_count < no_groups:
                self.group_name_LineEdit_container = np.append(
                    self.group_name_LineEdit_container, QtWidgets.QLineEdit()
                )
                self.device_assignment_LineEdit_container = np.append(
                    self.device_assignment_LineEdit_container, QtWidgets.QLineEdit()
                )
                self.group_colors_PushButton_container = np.append(
                    self.group_colors_PushButton_container, QtWidgets.QPushButton("")
                )
                self.group_colors_PushButton_container[-1].clicked.connect(
                    functools.partial(self.change_group_color, self.manual_group_count)
                )
                self.group_spectrum_PushButton_container = np.append(
                    self.group_spectrum_PushButton_container, QtWidgets.QPushButton("")
                )
                self.group_spectrum_PushButton_container[-1].clicked.connect(
                    functools.partial(self.change_spectrum, self.manual_group_count)
                )

                self.group_colors_PushButton_container[-1].setStyleSheet(
                    "background-color: "
                    + str(self.group_color[self.manual_group_count])
                )
                self.group_spectrum_PushButton_container[-1].setStyleSheet(
                    "background-color: red"
                )

                self.group_definition_gridLayout.addWidget(
                    self.group_name_LineEdit_container[-1],
                    np.size(self.group_name_LineEdit_container) + 1,
                    0,
                )
                self.group_definition_gridLayout.addWidget(
                    self.device_assignment_LineEdit_container[-1],
                    np.size(self.group_name_LineEdit_container) + 1,
                    1,
                )
                self.group_definition_gridLayout.addWidget(
                    self.group_spectrum_PushButton_container[-1],
                    np.size(self.group_name_LineEdit_container) + 1,
                    2,
                )
                self.group_definition_gridLayout.addWidget(
                    self.group_colors_PushButton_container[-1],
                    np.size(self.group_name_LineEdit_container) + 1,
                    3,
                )

                self.manual_group_count += 1

        elif self.manual_group_count > no_groups:
            while self.manual_group_count > no_groups:
                # All the following commands have to be applied to "properly"
                # delete widgets in PyQt.
                self.group_definition_gridLayout.removeWidget(
                    self.group_name_LineEdit_container[-1]
                )
                self.group_definition_gridLayout.removeWidget(
                    self.device_assignment_LineEdit_container[-1]
                )
                self.group_definition_gridLayout.removeWidget(
                    self.group_colors_PushButton_container[-1]
                )
                self.group_definition_gridLayout.removeWidget(
                    self.group_spectrum_PushButton_container[-1]
                )
                self.group_name_LineEdit_container[-1].setParent(None)
                self.group_name_LineEdit_container[-1] = None
                self.device_assignment_LineEdit_container[-1].setParent(None)
                self.device_assignment_LineEdit_container[-1] = None
                self.group_spectrum_PushButton_container[-1].setParent(None)
                self.group_spectrum_PushButton_container[-1] = None
                self.group_colors_PushButton_container[-1].setParent(None)
                self.group_colors_PushButton_container[-1] = None

                # Delete element from numpy array as well
                self.group_name_LineEdit_container = np.delete(
                    self.group_name_LineEdit_container,
                    np.size(self.group_name_LineEdit_container) - 1,
                )
                self.device_assignment_LineEdit_container = np.delete(
                    self.device_assignment_LineEdit_container,
                    np.size(self.device_assignment_LineEdit_container) - 1,
                )
                self.group_spectrum_PushButton_container = np.delete(
                    self.group_spectrum_PushButton_container,
                    np.size(self.group_spectrum_PushButton_container) - 1,
                )
                self.group_colors_PushButton_container = np.delete(
                    self.group_colors_PushButton_container,
                    np.size(self.group_colors_PushButton_container) - 1,
                )

                self.manual_group_count -= 1

    def change_spectrum(self, group_number):
        """
        Function that allows to change the color of a certain assigned group
        """
        global_variables = cf.read_global_settings()
        try:
            if os.path.isfile(self.group_spectrum_path[group_number]):
                initial_path = self.group_spectrum_path[group_number]
            else:
                initial_path = global_variables["default_saving_path"]
        except:
            initial_path = global_variables["default_saving_path"]

        file_path = QtWidgets.QFileDialog.getOpenFileName(
            QtWidgets.QFileDialog(),
            "Select a Folder",
            initial_path,
            "Text Files (*.csv *.txt)",
        )[0]

        # Now check if the select filepath is a valid one
        if os.path.isfile(file_path):
            self.group_spectrum_path[group_number] = file_path
            self.group_spectrum_PushButton_container[group_number].setStyleSheet(
                "background-color: green"
            )
        else:
            try:
                if os.path.isfile(self.group_spectrum_path[group_number]):
                    cf.log_message("Window closed without changing the file path")
                else:
                    self.group_spectrum_PushButton_container[
                        group_number
                    ].setStyleSheet("background-color: red")
                    cf.log_message(
                        self.group_spectrum_path[group_number]
                        + " is not a valid file path."
                    )
            except:
                self.group_spectrum_PushButton_container[group_number].setStyleSheet(
                    "background-color: red"
                )
                cf.log_message(
                    self.group_spectrum_path[group_number]
                    + " is not a valid file path."
                )

    def change_group_color(self, group_number):
        """
        Function that allows to change the color of a certain assigned group
        """
        # Change the color of the group by clicking on the button

        color = QtWidgets.QColorDialog.getColor()

        # Change the color of the push button according to the selection
        self.group_colors_PushButton_container[group_number].setStyleSheet(
            "background-color: " + str(color.name())
        )

        # Add the color to the list
        # print(color.name())
        if group_number < np.size(self.group_color):
            # print(group_number)
            self.group_color[group_number] = color.name()
        elif group_number > np.size(self.group_color):
            self.group_color = np.append(self.group_color, color.name())

    def close_without_saving(self):
        """
        Closes the window without saving
        """
        # Close window. Here I have to add a dialog that asks if the user
        # really wants to close without saving
        self.close()

    def save_groups(self):
        """
        Saves the assigned groups
        """

        group_names = []
        device_numbers_store = []

        for group_index in range(np.size(self.group_name_LineEdit_container)):
            # Now check if the user input was valid or not
            if self.device_assignment_LineEdit_container[group_index].text() == "":
                cf.log_message("Please enter device/s for your group. Try again!")
                return
            if self.device_assignment_LineEdit_container[group_index].text()[-1] == ",":
                cf.log_message(
                    "Please do not end your numbers with a comma. Try again!"
                )
                return
            # Now split the numbers that were entered in the QLineEdit for each group
            device_numbers = np.array(
                [
                    int(x)
                    for x in self.device_assignment_LineEdit_container[group_index]
                    .text()
                    .split(",")
                ]
            )
            if (
                np.all(
                    np.in1d(
                        device_numbers, np.unique(self.parameters["device_numbers"])
                    )
                )
                == False
            ):
                cf.log_message("Please only enter valid device numbers.")
                return

            if self.group_name_LineEdit_container[group_index].text() == "":
                cf.log_message("Please enter a valid group name.")
                return

            group_name = self.group_name_LineEdit_container[group_index].text()
            group_names.append(group_name)
            device_numbers_store.append(device_numbers)

        # Assign the variables that were calculated in this dialog
        self.parent.assigned_groups_df["group_name"] = group_names
        self.parent.assigned_groups_df["device_numbers"] = device_numbers_store
        self.parent.assigned_groups_df["spectrum_path"] = self.group_spectrum_path[
            0 : len(group_names)
        ]
        self.parent.assigned_groups_df["colors"] = self.group_color[
            0 : len(group_names)
        ]

        self.accept()
