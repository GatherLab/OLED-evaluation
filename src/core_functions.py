import logging
import json
import os.path
from pathlib import Path
import sys
import os
import subprocess
import pandas as pd


def log_message(message):
    """
    Function that manages the logging, in the sense that everything is
    directly logged into statusbar and the log file at once as well as
    printed to the console instead of having to call multiple functions.
    """
    # self.statusbar.showMessage(message, 10000000)
    logging.info(message)
    print(message)


def read_global_settings():
    """
    Read in global settings from file. The file can be changed using the
    settings window.
    """
    # Load from file to fill the lines
    with open(
        os.path.join(Path(__file__).parent.parent, "usr", "global_settings.json")
    ) as json_file:
        data = json.load(json_file)
    try:
        settings = data["overwrite"]

        # Update statusbar
        log_message("Global Settings Read from File")
    except:
        settings = data["default"]

        # Update statusbar
        log_message("Default device parameters taken")

    for key in settings[0].keys():
        try:
            settings[0][key] = float(settings[0][key])
        except:
            print("Entry not a float value")

    return settings[0]


def open_file(path):
    """
    Opens a file on the machine with the standard program
    https://stackoverflow.com/questions/6045679/open-file-with-pyqt
    """
    if sys.platform.startswith("linux"):
        subprocess.call(["xdg-open", path])
    else:
        os.startfile(path)


def read_file_names(folder_path):
    """
    Function that returns the names of all files in a certain folder at top
    level already sorted (does not go through all folder)
    """

    file_names = [
        file_path
        for file_path in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, file_path))
    ]

    return sorted(file_names)


def read_multiple_files(
    file_paths, column_names, file_synonyms, separator="\t", skip_row=0, skip_footer=0
):
    """
    Function that allows to read in data from a single or multiple files with
    the same column_names
    """
    data_frame = pd.DataFrame(columns=column_names, index=file_synonyms)

    i = 0
    for filename in file_paths:
        file_data_list = pd.read_csv(
            filename,
            skiprows=skip_row,
            skipfooter=skip_footer,
            sep=separator,
            names=column_names,
            engine="python",
            skip_blank_lines=False,
        )

        # Since we are readying in the data of multiple files, store this
        # differently in a pandas dataframe
        for name in column_names:
            data_frame[name].loc[file_synonyms[i]] = file_data_list[name].to_list()

        i += 1

    return data_frame


def save_file(df, file_path, header_lines, save_header=False):
    """
    Generic function that allows to save a file. If it exists already, rename
    it.
    """
    # First check if file already exists. If yes, add a number at the end (this
    # is checked as often as the file still exists to count up the numbers)
    i = 2
    while True:
        if not os.path.isfile(file_path):
            break

        # Get rid of file ending
        if i == 2:
            file_path = os.path.splitext(file_path)[0] + "_" + f"{i:02d}" + ".csv"
        else:
            # Since we already added a new _no to the file we have to get rid of it again
            file_path = "_".join(file_path.split("_")[:-1]) + "_" + f"{i:02d}" + ".csv"

        i += 1

    with open(file_path, "a") as the_file:
        the_file.write("\n".join(header_lines))

    # Now write pandas dataframe to file
    df.to_csv(file_path, index=False, mode="a", header=save_header, sep="\t")