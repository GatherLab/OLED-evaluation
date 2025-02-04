from PySide6 import QtWidgets
from UI_assign_group_window import Ui_AssignGroup

import os
import core_functions as cf
import functools

import numpy as np
import pandas as pd
import matplotlib as mpl


class AssignGroups(QtWidgets.QDialog, Ui_AssignGroup):
    """
    Settings window
    """

    def __init__(self, parameters, parent=None):
        QtWidgets.QDialog.__init__(self)
        self.parent = parent
        self.parameters = parameters

        global_variables = cf.read_global_settings()
        self.autodetect_spectrum = bool(global_variables["autodetect_spectrum"])
        self.include_all_scans = bool(global_variables["include_all_scans"])

        cmap = mpl.cm.get_cmap("Dark2", np.size(parameters["device_number"]))
        self.group_color = np.array(
            [mpl.colors.rgb2hex(cmap(i)) for i in range(cmap.N)], dtype=object
        )

        # self.group_color = np.array(
        # rand_color.generate(hue="blue", count=np.size(parameters["device_number"])),
        # dtype=object,
        # )
        self.group_spectrum_path = np.empty(
            np.size(parameters["device_number"]), dtype=object
        )

        # The manual group count is needed to keep track of the number of
        # groups being assigned
        self.manual_group_count = 1

        self.setupUi(self)

        # Connect functions to buttons
        self.no_groups_LabeledSlider.valueChanged(self.no_groups_slider_changed)
        if not self.autodetect_spectrum:
            self.group_spectrum_PushButton_container[0].clicked.connect(
                functools.partial(self.change_spectrum, 0)
            )
        self.group_colors_PushButton_container[0].clicked.connect(
            functools.partial(self.change_group_color, 0)
        )
        self.close_pushButton.clicked.connect(self.close_without_saving)
        self.save_pushButton.clicked.connect(self.save_groups)

        # Set the scan number of the combobox
        if not self.include_all_scans:
            idx = self.select_scan_number_ComboBox.findText(
                str(self.parameters["selected_scan_number"])
            )
            if idx >= 0:
                self.select_scan_number_ComboBox.setCurrentIndex(idx)

        # self.select_scan_number_ComboBox.setCurrentIndex(
        #     self.parameters["selected_scan_number"]
        # )

        # In case groups were already assigned the dialog should be directly
        # initalised with those groups
        groups = self.parameters["assigned_groups_df"]["group_name"].unique()
        if len(groups) > 0:

            self.no_groups_LabeledSlider.setValue(len(groups))
            self.no_groups_slider_changed()
            i = 0

            for group in groups:
                self.group_name_LineEdit_container[i].setText(group)

                self.device_assignment_LineEdit_container[i].setText(
                    ",".join(
                        map(
                            str,
                            self.parameters["assigned_groups_df"]
                            .loc[
                                self.parameters["assigned_groups_df"]["group_name"]
                                == group
                            ]
                            .index.to_list(),
                        )
                    )
                )
                self.group_spectrum_path[i] = (
                    self.parameters["assigned_groups_df"]
                    .loc[self.parameters["assigned_groups_df"]["group_name"] == group][
                        "spectrum_path"
                    ]
                    .to_list()[0]
                )

                self.group_color[i] = (
                    self.parameters["assigned_groups_df"]
                    .loc[self.parameters["assigned_groups_df"]["group_name"] == group][
                        "color"
                    ]
                    .to_list()[0]
                )
                try:
                    if not self.autodetect_spectrum:
                        if os.path.isfile(self.group_spectrum_path[i]):
                            self.group_spectrum_PushButton_container[i].setStyleSheet(
                                "background-color: green"
                            )
                except:
                    cf.log_message(
                        "Spectrum file for group "
                        + str(group)
                        + " could not be loaded. Please set again."
                    )

                self.group_colors_PushButton_container[i].setStyleSheet(
                    "background-color: " + str(self.group_color[i])
                )
                i += 1

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
                if not self.autodetect_spectrum:
                    self.group_spectrum_PushButton_container = np.append(
                        self.group_spectrum_PushButton_container,
                        QtWidgets.QPushButton(""),
                    )
                    self.group_spectrum_PushButton_container[-1].clicked.connect(
                        functools.partial(self.change_spectrum, self.manual_group_count)
                    )
                    self.group_spectrum_PushButton_container[-1].setStyleSheet(
                        "background-color: red"
                    )
                    self.group_definition_gridLayout.addWidget(
                        self.group_spectrum_PushButton_container[-1],
                        np.size(self.group_name_LineEdit_container) + 1,
                        2,
                    )

                self.group_colors_PushButton_container[-1].setStyleSheet(
                    "background-color: "
                    + str(self.group_color[self.manual_group_count])
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
                if not self.autodetect_spectrum:
                    self.group_definition_gridLayout.removeWidget(
                        self.group_spectrum_PushButton_container[-1]
                    )
                    self.group_spectrum_PushButton_container[-1].setParent(None)
                    self.group_spectrum_PushButton_container[-1] = None
                    self.group_spectrum_PushButton_container = np.delete(
                        self.group_spectrum_PushButton_container,
                        np.size(self.group_spectrum_PushButton_container) - 1,
                    )

                self.group_name_LineEdit_container[-1].setParent(None)
                self.group_name_LineEdit_container[-1] = None
                self.device_assignment_LineEdit_container[-1].setParent(None)
                self.device_assignment_LineEdit_container[-1] = None
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
            if os.path.isfile(str(self.group_spectrum_path[group_number])):
                initial_path = self.group_spectrum_path[group_number]
            else:
                initial_path = self.parent.global_path
        except:
            initial_path = global_variables["default_saving_path"]

        file_path = QtWidgets.QFileDialog.getOpenFileName(
            QtWidgets.QFileDialog(),
            "Select a Folder",
            initial_path,
            "Spectrum Files (*_spec*.csv *_gon-spec*.csv)",
        )[0]

        # Now check if the select filepath is a valid one
        if os.path.isfile(file_path):
            self.group_spectrum_path[group_number] = file_path
            if not self.autodetect_spectrum:
                self.group_spectrum_PushButton_container[group_number].setStyleSheet(
                    "background-color: green"
                )
        else:
            try:
                if os.path.isfile(self.group_spectrum_path[group_number]):
                    cf.log_message("Window closed without changing the file path")
                else:
                    if not self.autodetect_spectrum:
                        self.group_spectrum_PushButton_container[
                            group_number
                        ].setStyleSheet("background-color: red")
                    cf.log_message(
                        self.group_spectrum_path[group_number]
                        + " is not a valid file path."
                    )
            except:
                if not self.autodetect_spectrum:
                    self.group_spectrum_PushButton_container[
                        group_number
                    ].setStyleSheet("background-color: red")
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

    def autodetect_matching_spectrum(self):
        """
        Function that allows the automatic detection of the right spectru function.
        """
        files_df = pd.DataFrame()
        file_names = self.parent.file_names

        spec_file_names = []
        dates = []
        batch_names = []
        spec_file_names = []
        device_numbers = []
        pixel_numbers = []
        ar_spectrum = []
        scan_number = []
        identifier = []

        for name in file_names:
            split_name = name.split("_")
            if len(split_name) == 5:
                if str(split_name[4].split(".")[0]) not in ["spec", "gon-spec"]:
                    continue
                # Right file name but only one scan
                spec_file_names.append(name)
                dates.append(str(split_name[0]))
                batch_names.append(str(split_name[1]))
                device_numbers.append(int(split_name[2][1:]))
                pixel_numbers.append(int(split_name[3].split(".")[0][1:]))
                scan_number.append(1)
                identifier.append(split_name[2] + split_name[3].split(".")[0] + "s1")
                if str(split_name[4].split(".")[0]) == "gon-spec":
                    ar_spectrum.append(True)
                else:
                    ar_spectrum.append(False)
            elif len(split_name) == 6:
                if str(split_name[4].split(".")[0]) not in ["spec", "gon-spec"]:
                    continue
                # If this is > first scan
                spec_file_names.append(name)
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
                if str(split_name[4].split(".")[0]) == "gon-spec":
                    ar_spectrum.append(True)
                else:
                    ar_spectrum.append(False)
            # else:
            #     # File name is not in the correct format
            #     cf.log_message(
            #         "The file name does not follow the naming convention date_batch-name_d<no>_p<no>_<no>.csv"
            #     )
        # if np.size(np.unique(batch_names)) > 1:
        #     cf.log_message(
        #         "The batch name does not match for all files. If there are different OLEDs with the same device number this could lead to a problem."
        #     )

        files_df["file_name"] = spec_file_names
        files_df["device_number"] = device_numbers
        files_df["pixel_number"] = pixel_numbers
        files_df["scan_number"] = scan_number
        files_df["ar_spectrum"] = ar_spectrum

        for index, data in self.parent.assigned_groups_df.iterrows():
            # Search for spectrum of very same pixel

            # Search for spectrum of same device
            # Try to get an angle resolved spectrum
            spectrum_path_device = files_df.loc[
                np.logical_and(
                    files_df.ar_spectrum, files_df["device_number"] == data.name
                ),
                "file_name",
            ]

            # If there is none, try to get any spectrum
            if len(spectrum_path_device) == 0:
                spectrum_path_device = files_df.loc[
                    files_df["device_number"] == data.name, "file_name"
                ]
            else:
                cf.log_message("Angle resolved spectrum found for device " + str(index))

            spectrum_path = (
                self.parent.global_path + "/" + next(iter(spectrum_path_device), "")
            )

            # Search for spectrum of same group
            if len(spectrum_path_device) == 0:
                group_name = self.parent.assigned_groups_df.loc[
                    self.parent.assigned_groups_df.index == data.name, "group_name"
                ].item()

                devices_in_group = self.parent.assigned_groups_df.loc[
                    self.parent.assigned_groups_df.group_name == group_name
                ].index.to_list()

                # Try to get an angle resolved spectrum
                spectrum_path_list = (
                    files_df.loc[
                        np.logical_and(
                            files_df.ar_spectrum,
                            files_df["device_number"].isin(devices_in_group),
                        ),
                        "file_name",
                    ]
                ).to_list()

                # If there is none, try to get any spectrum
                if len(spectrum_path_list) == 0:
                    spectrum_path_list = (
                        files_df.loc[
                            files_df["device_number"].isin(devices_in_group),
                            "file_name",
                        ]
                    ).to_list()

                else:
                    cf.log_message(
                        "Angle resolved spectrum found for device " + str(index)
                    )

                # Only return first item of that list (if it exists)
                spectrum_path = (
                    self.parent.global_path + "/" + next(iter(spectrum_path_list), "")
                )

            # Show error if non of the above was found in the according folder
            if len(spectrum_path) == self.parent.global_path + "/":
                cf.log_message(
                    "No spectrum found for device "
                    + str(data.name)
                    + " pixel "
                    + str(data["pixel_number"])
                )

            # Assign spectrum path to dataframe
            self.parent.assigned_groups_df.loc[index].spectrum_path = spectrum_path

    def save_groups(self):
        """
        Saves the assigned groups
        """

        # Empty the relevant dataframe first so that no multiple entries are made
        self.parent.assigned_groups_df = self.parent.assigned_groups_df[0:0]

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
                    np.in1d(device_numbers, np.unique(self.parameters["device_number"]))
                )
                == False
            ):
                cf.log_message("Please only enter valid device numbers.")
                return

            if self.group_name_LineEdit_container[group_index].text() == "":
                cf.log_message("Please enter a valid group name.")
                return

            group_name = self.group_name_LineEdit_container[group_index].text()

            # Now generate for each device a seperate row in our pandas dataframe
            for number in device_numbers:
                self.parent.assigned_groups_df = pd.concat(
                    [
                        self.parent.assigned_groups_df,
                        pd.DataFrame(
                            {
                                "group_name": [group_name],
                                "spectrum_path": [
                                    self.group_spectrum_path[group_index]
                                ],
                                "color": [self.group_color[group_index]],
                            }
                        ),
                    ],
                    ignore_index=True,
                )

            # group_names.append(group_name)
            device_numbers_store.append(device_numbers)

        # Assign the variables that were calculated in this dialog
        # self.parent.assigned_groups_df.set_index(group_names)
        # self.parent.assigned_groups_df["device_number"] = device_numbers_store
        # self.parent.assigned_groups_df["spectrum_path"] = self.group_spectrum_path[
        #     0 : len(group_names)
        # ]
        # self.parent.assigned_groups_df["color"] = self.group_color[0 : len(group_names)]

        # Assign scan number
        if not self.include_all_scans:
            self.parent.selected_scan = int(
                self.select_scan_number_ComboBox.currentText()
            )
        else:
            # If all scans were selected instead, make it zero (because there is
            # no zero-th scan)
            self.parent.selected_scan = 0

        # Finally, set the indexes to the device numbers
        self.parent.assigned_groups_df = self.parent.assigned_groups_df.set_index(
            np.concatenate(device_numbers_store)
        )

        # If autodetection of the spectra was chosen, do so
        if self.autodetect_spectrum:
            self.autodetect_matching_spectrum()

        self.accept()
