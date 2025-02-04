from PySide6 import QtWidgets

import numpy as np
import functools
from UI_show_group_window import Ui_ShowGroup


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
                    self.parent.plot_from_device_number,
                    self.parameters["device_number"][index],
                )
            )

        for index in range(np.size(self.parameters["group_name"])):
            # Connect the push buttons for the group buttons
            self.group_pushButton_container[index].clicked.connect(
                functools.partial(
                    self.parent.plot_from_group_name,
                    self.parameters["group_name"][index],
                )
            )

        self.close_pushButton.clicked.connect(self.close)

    def close(self):
        """
        Closes the dialog
        """
        self.accept()
