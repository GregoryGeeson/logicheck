#!/usr/bin/env python

"""
logicheck.py

Copyright 2016 Ben Cottier

This file is part of Logicheck.

Logicheck is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Logicheck is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Logicheck.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFont

from argument import ArgCheck
from resource_path import resource_path


class Logicheck(QMainWindow):
    """The main window for the application.
    """

    def __init__(self):
        """
        Constructor
        """

        # Inherit from QMainWindow.
        super().__init__()

        # Top-level config:
        self.setCentralWidget(ArgCheck(self))
        # Set relative window position (first two args) and size.
        self.setGeometry(50, 80, 425, 540)
        self.setWindowTitle("Logicheck")
        self.setWindowIcon(QIcon(resource_path("images/logicheck_icon_3.png")))

        # Create menu.
        # Create a help action which will go in a drop-down menu.
        # The "&" in "&Help" specifies the Alt- shortcut key.
        helpAction = QAction(QIcon(resource_path("images/logicheck_help_icon.png")),
                             "&Help", self)
        helpAction.setShortcut("Ctrl+H")
        # Connect the selection of the action to displaying the manual
        helpAction.triggered.connect(self.show_info)
        # Create the status bar and the menu bar
        self.statusBar()
        menubar = self.menuBar()
        helpMenu = menubar.addMenu("&Help")
        # Link the menu item to the action.
        helpMenu.addAction(helpAction)

    def show_info(self):
        # Create window displaying the manual.
        info_file = open(resource_path("documents/manual.html"))
        # Get the contents (text).
        info = info_file.read()
        self.info_window = ManualWindow(info)
        font1 = QFont()
        font1.setPointSize(11)
        self.info_window.setFont(font1)
        self.info_window.setWindowIcon(QIcon(resource_path(
            "images/logicheck_icon_3.png")))
        self.info_window.show()


class ManualWindow(QMainWindow):
    """The window for displaying the operation manual.
    """

    def __init__(self, info):
        """
        Constructor
        """

        super().__init__()

        # Create object to display text.
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setText(info)
        # Create layout to store text object.
        info_layout = QGridLayout()
        info_layout.addWidget(info_text, 0, 0)
        info_widget = QWidget()
        info_widget.setLayout(info_layout)

        self.setCentralWidget(info_widget)
        self.setGeometry(80, 110, 425, 540)
        self.setWindowTitle("Logicheck - Manual")
        self.setWindowIcon(QIcon("images/logicheck_icon_3.png"))

# Create window.
# Execute the program only if the file was run directly, not imported.
if __name__ == "__main__":
    # Create application object.
    # "sys.argv" is a list of args from the command line.
    # This allows controlled startup from the shell.
    app = QApplication(sys.argv)
    # Initialise main window and display it.
    window = Logicheck()
    window.show()
    # Enter the mainloop, which exits if exit() is called or the main widget
    # is destroyed. This gives a clean exit, with exit code.
    sys.exit(app.exec_())
