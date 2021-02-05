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

from UI_show_group import Ui_ShowGroup


class ShowGroup(QtWidgets.QDialog, Ui_ShowGroup):
    """
    Settings window
    """

    def __init__(self, parameters, parent=None):
        QtWidgets.QDialog.__init__(self)
        self.parent = parent
        self.parameters = parameters
        self.setupUi(self)

        # Connect functions to buttons
        for index in range(len(self.parameters["device_number"])):
            # Connect the push button to the right function
            self.device_pushButton_container[index].clicked.connect(
                functools.partial(
                    self.parent.plot_device, self.parameters["device_number"][index]
                )
            )

        for index in range(np.size(self.parameters["group_name"])):
            # Connect the push buttons for the group buttons
            self.group_pushButton_container[index].clicked.connect(
                functools.partial(
                    self.parent.plot_group, self.parameters["group_name"][index]
                )
            )

        self.close_pushButton.clicked.connect(self.close)

    def show_device(self, device_number):
        """
        Function that triggers a plotting of the JVL curve of a certain
        device in the main window
        """
        print("Show group")

    def show_group(self, group_name):
        """
        Function that triggers a plotting of the JVL curve of a certain
        device in the main window
        """
        print("Show group")

    def close(self):
        """
        Closes the dialog
        """
        self.accept()
