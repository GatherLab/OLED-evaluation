from PySide6 import QtCore, QtWidgets

import numpy as np


class Ui_ShowHeros(object):
    def setupUi(self, ShowHeros):
        # Note: this is not how it should be done but currently I don't know
        # how to do it differently. This is only needed to be able to emit
        # signals to the main window

        ShowHeros.setObjectName("ShowHeros")
        ShowHeros.setWindowTitle("Show Heros Dialog")
        ShowHeros.resize(400, 100)
        ShowHeros.setStyleSheet(
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
        self.verticalLayout = QtWidgets.QVBoxLayout(ShowHeros)
        self.verticalLayout.setContentsMargins(25, 10, 25, 10)
        self.verticalLayout.setObjectName("verticalLayout")

        # Define dialog in which parameters should be entered
        # dialog = QtWidgets.QDialog()
        # dialog.setWindowTitle("Show Heros Dialog")

        # Define all the layouts and labels so that the window looks good
        # verticalLayout = QtWidgets.QVBoxLayout()
        self.header_label = QtWidgets.QLabel()
        self.header_label.setObjectName("header_label")
        self.verticalLayout.addWidget(self.header_label)

        self.devices_label = QtWidgets.QLabel()
        self.devices_label.setObjectName("devices_label")
        self.verticalLayout.addWidget(self.devices_label)

        # verticalLayout.addWidget(
        # QtWidgets.QLabel("IV Curves of which group or device shall be plotted?")
        # )
        # verticalLayout.addWidget(QtWidgets.QLabel("Light IV"))

        # Grid Layout that hosts push buttons for the different devices
        # self.devices_gridLayout = QtWidgets.QGridLayout()
        # self.device_pushButton_container = np.empty(0, dtype="object")

        # Count the number of pushbuttons in a row to have a line break every
        # max_row push buttons
        self.heros_QHBoxLayout = QtWidgets.QHBoxLayout()
        count_row = 0
        max_row = 6

        # Generate the same number of push buttons than nb of devices
        # for index in range(len(self.parameters["device_number"])):
        #     # Add pushbutton to pushbutton container with the right device number
        #     self.device_pushButton_container = np.append(
        #         self.device_pushButton_container,
        #         QtWidgets.QPushButton(
        #             str(int(self.parameters["device_number"][index]))
        #         ),
        #     )

        #     # # Connect the push button to the right function
        #     # self.device_pushButton_container[index].clicked.connect(
        #     #     functools.partial(
        #     #         self.showHeros, self.parameters["device_number"][index]
        #     #     )
        #     # )

        #     # Add pushbutton to the grid layout
        #     self.devices_gridLayout.addWidget(
        #         self.device_pushButton_container[-1],
        #         int(count_row / max_row),
        #         (np.size(self.device_pushButton_container) - 1) % max_row,
        #     )

        #     count_row += 1
        # self.device_pushButton_container = np.append(
        self.plot_all_selected = QtWidgets.QPushButton("All Selected")
        self.plot_max_luminance = QtWidgets.QPushButton("Max Luminance")
        self.plot_max_eqe = QtWidgets.QPushButton("Max EQE")

        self.heros_QHBoxLayout.addWidget(self.plot_all_selected)
        self.heros_QHBoxLayout.addWidget(self.plot_max_luminance)
        self.heros_QHBoxLayout.addWidget(self.plot_max_eqe)

        self.verticalLayout.addLayout(self.heros_QHBoxLayout)

        # If group names were already defined do the same for the groups
        if np.size(self.parameters["group_name"]) > 0:
            # Add a header label for the groups
            self.group_label = QtWidgets.QLabel()
            self.group_label.setObjectName("group_label")
            self.verticalLayout.addWidget(self.group_label)

            # self.labelHeros = QtWidgets.QLabel("Heros:")
            # verticalLayout.addWidget(self.labelHeros)
            self.groups_gridLayout = QtWidgets.QGridLayout()
            self.group_pushButton_container = np.empty(0, dtype="object")

            # have a line break every max_row push buttons
            count_row = 0

            for index in range(np.size(self.parameters["group_name"])):
                # Append a pushbutton for each group
                self.group_pushButton_container = np.append(
                    self.group_pushButton_container,
                    QtWidgets.QPushButton(str(self.parameters["group_name"][index])),
                )

                # Add pushbuttons to grid layout
                self.groups_gridLayout.addWidget(
                    self.group_pushButton_container[-1],
                    int(count_row / max_row),
                    (np.size(self.group_pushButton_container) - 1) % max_row,
                )
                count_row += 1

            self.verticalLayout.addLayout(self.groups_gridLayout)

        # Add an exit button to the dialog
        self.close_pushButton = QtWidgets.QPushButton("Close")

        self.verticalLayout.addWidget(self.close_pushButton)

        self.setLayout(self.verticalLayout)

        self.retranslateUi(ShowHeros)
        QtCore.QMetaObject.connectSlotsByName(ShowHeros)

    def retranslateUi(self, ShowHeros):
        _translate = QtCore.QCoreApplication.translate
        ShowHeros.setWindowTitle(_translate("ShowHeros", "Show Heros"))

        self.header_label.setText(
            _translate("ShowHeros", "Select Heros or Groups to Plot")
        )
        self.devices_label.setText(_translate("ShowHeros", "Heros"))
        self.group_label.setText(_translate("ShowHeros", "Groups"))
