from PySide6 import QtWidgets

import functools
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
