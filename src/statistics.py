# -*- coding: utf-8 -*-
from PySide2 import QtCore, QtGui, QtWidgets

import json
import os
import core_functions as cf
from pathlib import Path
import functools

import numpy as np
import pandas as pd

# import randomcolor

from UI_statistics_window import Ui_Statistics


class Statistics(QtWidgets.QDialog, Ui_Statistics):
    """
    Settings window
    """

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self)
        self.parent = parent
        self.setupUi(self)

        # Connect functions to buttons
        self.statistics_by_device_pushButton.clicked.connect(
            functools.partial(self.parent.show_statistics, groupby="device_number")
        )
        self.statistics_by_group_pushButton.clicked.connect(
            functools.partial(self.parent.show_statistics, groupby="group_name")
        )
        self.close_pushButton.clicked.connect(self.close)

    def close(self):
        """
        Closes the dialog
        """
        self.accept()
