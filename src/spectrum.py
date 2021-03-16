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

from UI_spectrum_window import Ui_EvaluateSpectrum


class EvaluateSpectrum(QtWidgets.QDialog, Ui_EvaluateSpectrum):
    """
    Settings window
    """

    def __init__(self, parameters, parent=None):
        QtWidgets.QDialog.__init__(self)
        self.parent = parent
        self.parameters = parameters
        self.setupUi(self)

        for index in range(np.size(self.parameters["group_name"])):
            # Connect the push buttons for the group buttons
            self.group_pushButton_container[index].clicked.connect(
                functools.partial(
                    self.parent.plot_spectrum,
                    self.parameters["group_name"][index],
                )
            )

        self.close_pushButton.clicked.connect(self.close)

    def close(self):
        """
        Closes the dialog
        """
        self.accept()
