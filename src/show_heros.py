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

from UI_show_heros_window import Ui_ShowHeros


class ShowHeros(QtWidgets.QDialog, Ui_ShowHeros):
    """
    Show heros window
    """

    def __init__(self, parameters, parent=None):
        QtWidgets.QDialog.__init__(self)
        self.parent = parent
        self.parameters = parameters
        self.setupUi(self)

        # # Connect functions to buttons
        # for index in range(len(self.parameters["device_number"])):
        #     # Connect the push button to the right function
        #     self.device_pushButton_container[index].clicked.connect(
        #         functools.partial(
        #             self.parent.plot_from_device_number,
        #             self.parameters["device_number"][index],
        #         )
        #     )

        self.plot_all_selected.clicked.connect(
            functools.partial(
                self.parent.plot_four_graphs,
                self.parent.data_df.loc[
                    self.parent.data_df.masked == False
                ].index.to_list(),
                False,
            )
        )

        # Find out the pixel of maximum luminance and maximum eqe for each group
        luminance_list = []
        eqe_list = []
        for group_name in self.parameters["group_name"]:
            # Temporal data frame to make it easier to determine the entry of
            # maximum luminance and eqe
            temp_df = self.parent.data_df.join(
                self.parent.assigned_groups_df, on="device_number"
            )
            temp_data = temp_df.loc[
                np.logical_and(
                    temp_df["group_name"] == group_name,
                    temp_df.masked == False,
                )
            ]
            # Obtain entry with maximum luminance for each group
            luminance_list.append(
                temp_data.iloc[
                    np.argmax([max(x) for x in temp_data.luminance.values])
                ].name
            )
            # Obtain entry with maximum eqe for each group
            eqe_list.append(
                temp_data.iloc[np.argmax([max(x) for x in temp_data.eqe.values])].name
            )

        self.plot_max_luminance.clicked.connect(
            functools.partial(self.parent.plot_four_graphs, luminance_list)
        )

        self.plot_max_eqe.clicked.connect(
            functools.partial(self.parent.plot_four_graphs, eqe_list)
        )

        for index in range(np.size(self.parameters["group_name"])):
            # Connect the push buttons for the group buttons
            temp_df = self.parent.data_df.join(
                self.parent.assigned_groups_df, on="device_number"
            )
            self.group_pushButton_container[index].clicked.connect(
                functools.partial(
                    self.parent.plot_four_graphs,
                    temp_df.loc[
                        np.logical_and(
                            temp_df.group_name == self.parameters["group_name"][index],
                            temp_df.masked == False,
                        )
                    ].index.to_list(),
                    False,
                )
            )

        self.close_pushButton.clicked.connect(self.close)

    def close(self):
        """
        Closes the dialog
        """
        self.accept()
