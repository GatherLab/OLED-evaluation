import logging
import json
import os.path
from pathlib import Path
import sys
import os
import subprocess


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
