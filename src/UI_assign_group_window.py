from PySide6 import QtCore, QtWidgets

import numpy as np
from UI_labeled_slider import LabeledSlider


class Ui_AssignGroup(object):
    def setupUi(self, AssignGroups):
        # Note: this is not how it should be done but currently I don't know
        # how to do it differently. This is only needed to be able to emit
        # signals to the main window

        AssignGroups.setObjectName("AssignGroups")
        AssignGroups.setWindowTitle("Group Assignement Dialog")
        AssignGroups.resize(509, 317)
        AssignGroups.setStyleSheet(
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
        self.verticalLayout = QtWidgets.QVBoxLayout(AssignGroups)
        self.verticalLayout.setContentsMargins(25, 10, 25, 10)
        self.verticalLayout.setObjectName("verticalLayout")

        # # Device settings
        # self.device_settings_header_label = QtWidgets.QLabel(AssignGroups)
        # self.device_settings_header_label.setMinimumSize(QtCore.QSize(0, 20))
        # self.device_settings_header_label.setStyleSheet(
        #     'font: 75 bold 10pt "Segoe UI";'
        # )
        # self.device_settings_header_label.setObjectName("device_settings_header_label")
        # self.verticalLayout.addWidget(self.device_settings_header_label)

        # self.header_line_1 = QtWidgets.QFrame()
        # self.header_line_1.setFrameShape(QtWidgets.QFrame.HLine)
        # self.header_line_1.setFrameShadow(QtWidgets.QFrame.Sunken)
        # self.verticalLayout.addWidget(self.header_line_1)
        # self.header_line_1.setStyleSheet(
        #     "QFrame {\n" "            border: 2px solid rgb(52, 59, 72);\n" "}\n"
        # )

        # self.manualRowCountGridLayout = 1

        # Define dialog in which parameters should be entered
        # dialog = QtWidgets.QDialog()
        # dialog.setWindowTitle("Group Assignement Dialog")

        # Select the scan that shall be evaluated
        if not self.include_all_scans:
            self.select_scan_number_label = QtWidgets.QLabel()
            self.select_scan_number_label.setObjectName("select_scan_number_label")
            self.verticalLayout.addWidget(self.select_scan_number_label)

            self.select_scan_number_ComboBox = QtWidgets.QComboBox()
            self.select_scan_number_ComboBox.setObjectName(
                "select_scan_number_ComboBox"
            )

            for i in range(self.parameters["no_of_scans"]):
                self.select_scan_number_ComboBox.addItem(str(int(i + 1)))

            self.select_scan_number_ComboBox.setCurrentIndex(0)
            self.verticalLayout.addWidget(self.select_scan_number_ComboBox)

        # Select the number of groups to define
        self.no_groups_label = QtWidgets.QLabel()
        self.verticalLayout.addWidget(self.no_groups_label)

        self.no_groups_LabeledSlider = LabeledSlider(
            1,
            int(np.size(np.unique(self.parameters["device_number"]))),
            interval=1,
            orientation=QtCore.Qt.Horizontal,
        )

        self.verticalLayout.addWidget(self.no_groups_LabeledSlider)

        self.available_devices_label = QtWidgets.QLabel()
        self.verticalLayout.addWidget(self.available_devices_label)

        # if np.size(self.paths) == 1:
        # verticalLayout.addWidget(self.no_groups_LabeledSlider)

        # Define the group assignement fields
        self.group_definition_gridLayout = QtWidgets.QGridLayout()
        self.group_definition_gridLayout.setSpacing(10)

        # Group names and its container
        self.group_name_label = QtWidgets.QLabel()
        self.group_definition_gridLayout.addWidget(self.group_name_label, 1, 0, 1, 1)

        self.group_name_LineEdit_container = np.empty(0, dtype="object")
        self.group_name_LineEdit_container = np.append(
            self.group_name_LineEdit_container, QtWidgets.QLineEdit()
        )
        self.group_definition_gridLayout.addWidget(
            self.group_name_LineEdit_container[0], 2, 0
        )

        # Enter device numbers and its container
        self.device_assignment_label = QtWidgets.QLabel()
        self.group_definition_gridLayout.addWidget(
            self.device_assignment_label, 1, 1, 1, 1
        )

        self.device_assignment_LineEdit_container = np.empty(0, dtype="object")
        self.device_assignment_LineEdit_container = np.append(
            self.device_assignment_LineEdit_container, QtWidgets.QLineEdit()
        )
        self.group_definition_gridLayout.addWidget(
            self.device_assignment_LineEdit_container[0], 2, 1
        )

        # Assign a spectrum file to the group
        if not self.autodetect_spectrum:
            self.spectrum_file_label = QtWidgets.QLabel()
            self.group_definition_gridLayout.addWidget(
                self.spectrum_file_label, 1, 2, 1, 1
            )

            self.group_spectrum_PushButton_container = np.empty(0, dtype="object")
            self.group_spectrum_PushButton_container = np.append(
                self.group_spectrum_PushButton_container, QtWidgets.QPushButton("")
            )
            self.group_spectrum_PushButton_container[0].setStyleSheet(
                "background-color: red"
            )
            self.group_definition_gridLayout.addWidget(
                self.group_spectrum_PushButton_container[0], 2, 2
            )

        # Definition of a plotting color for the group
        self.group_color_label = QtWidgets.QLabel()
        self.group_definition_gridLayout.addWidget(self.group_color_label, 1, 3, 1, 1)
        self.group_colors_PushButton_container = np.empty(0, dtype="object")
        self.group_colors_PushButton_container = np.append(
            self.group_colors_PushButton_container, QtWidgets.QPushButton("")
        )
        self.group_colors_PushButton_container[0].setStyleSheet(
            "background-color: " + str(self.group_color[0])
        )
        self.group_definition_gridLayout.addWidget(
            self.group_colors_PushButton_container[0], 2, 3
        )

        # Define the bottom pushbuttons that allows to close and save the dialog
        self.leave_horizontalLayout = QtWidgets.QHBoxLayout()
        self.close_pushButton = QtWidgets.QPushButton("Close")

        self.save_pushButton = QtWidgets.QPushButton("Save")

        self.leave_horizontalLayout.addWidget(self.close_pushButton)
        self.leave_horizontalLayout.addWidget(self.save_pushButton)

        self.verticalLayout.addLayout(self.group_definition_gridLayout)
        self.verticalLayout.addLayout(self.leave_horizontalLayout)

        self.setLayout(self.verticalLayout)

        self.retranslateUi(AssignGroups)
        QtCore.QMetaObject.connectSlotsByName(AssignGroups)

    def retranslateUi(self, AssignGroups):
        _translate = QtCore.QCoreApplication.translate
        AssignGroups.setWindowTitle(_translate("AssignGroups", "Assign Groups"))

        if not self.include_all_scans:
            self.select_scan_number_label.setText(
                _translate("AssignGroups", "Select Scan")
            )
        self.no_groups_label.setText(
            _translate("AssignGroups", "Select Number of Groups")
        )
        self.available_devices_label.setText(
            _translate(
                "AssignGroups",
                "Available Devices for Assignment "
                + str(self.parameters["device_number"]),
            )
        )
        self.group_name_label.setText(_translate("AssignGroups", "Group Name"))
        self.device_assignment_label.setText(
            _translate("AssignGroups", "Assign Devices (seperated by ,)")
        )
        self.group_color_label.setText(_translate("AssignGroups", "Color"))
        if not self.autodetect_spectrum:
            self.spectrum_file_label.setText(_translate("AssignGroups", "Spectrum"))
