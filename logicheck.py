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


class Logicheck(QMainWindow):
    def __init__(self):
        """
        Constructor
        """

        super().__init__()

        # top-level config
        self.setCentralWidget(ArgCheck(self))
        self.setGeometry(50, 80, 425, 540)
        self.setWindowTitle("Logicheck")
        self.setWindowIcon(QIcon("logicheck/images/logicheck_icon_3.png"))

        # create menu
        helpAction = QAction(QIcon("logicheck/images/logicheck_help_icon.png"),
                             "&Help", self)
        helpAction.setShortcut("Ctrl+H")
        helpAction.triggered.connect(self.show_info)
        self.statusBar()
        menubar = self.menuBar()
        helpMenu = menubar.addMenu("&Help")
        helpMenu.addAction(helpAction)

    def show_info(self):
        # create about window
        info_file = open("logicheck/documents/manual.txt", encoding="utf-8")
        info = info_file.read()
        self.info_window = ManualWindow(info)
        font1 = QFont()
        font1.setPointSize(11)
        self.info_window.setFont(font1)
        self.info_window.show()


class ManualWindow(QMainWindow):

    def __init__(self, info):
        """
        Constructor
        """

        super().__init__()

        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setText(info)
        info_layout = QGridLayout()
        info_layout.addWidget(info_text, 0, 0)
        info_widget = QWidget()
        info_widget.setLayout(info_layout)

        self.setCentralWidget(info_widget)
        self.setGeometry(80, 110, 425, 540)
        self.setWindowTitle("Logicheck - Manual")
        self.setWindowIcon(QIcon("logicheck/images/logicheck_icon_3.png"))

# create window
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Logicheck()
    window.show()
    sys.exit(app.exec_())


# ERROR LOG:
    # Manual window causes crash when run using python.exe


