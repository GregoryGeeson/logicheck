#!/usr/bin/env python

"""
ArgTab.py

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

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon


class TruthTable(object):
    """Handles the display of truth tables and the associated data.
    """

    def __init__(self, symbols, premises, symbol_truth, premise_truth,
                 conc=True):
        """
        Constructor

        __init__(list<str>, list<str>, list<str>, list<list<int>>, bool)
        """

        self.symbols = symbols
        self.premises = premises
        self.symbol_truth = symbol_truth
        self.premise_truth = premise_truth
        self.conc = conc

        self.generate_table_data()

    def generate_table_data(self):
        """Processes the data for the table and sorts it into a list mirroring
        the table structure.
        """

        # Convert elements of premise_truth from int to str in a new list.
        self.conversion = []
        for i in range(len(self.premise_truth)):
            self.sub_list = []
            for j in range(len(self.premise_truth[i])):
                self.sub_list.append(str(self.premise_truth[i][j]))
            self.conversion.append(self.sub_list)

        l = len(self.premises)
        premises2 = []

        # Format logical expressions for column headings in a new list.
        for i in range(l):
            if i == l - 1 and self.conc:
                # Prepend a "therefore" symbol to the conclusion.
                premises2.append("".join([u'\u2234', "    ",
                                          self.premises[-1]]))
            else:
                # Prepend a number to the expression.
                premises2.append("".join([str(i+1), ".    ",
                                          self.premises[i]]))

        # First row of table data - symbols then premises as column headings.
        self.table_data = [self.symbols]
        self.table_data[0].extend(premises2)

        # Create the remaining rows of truth values, i.e. 1's and 0's.
        for i in range(len(self.symbol_truth)):
            self.table_row = []
            for j in range(len(self.symbol_truth[i])):
                self.table_row.append(self.symbol_truth[i][j])
            self.table_row.extend(self.conversion[i])
            self.table_data.append(self.table_row)

        # E.g.
        # symbol_truth = [('0', '0', '1'), ...]
        # premise_truth = [[1, 0, 1], ...]
        # table = [ ['A', 'B', 'C', 'A->B', 'C+A', 'B'],
        # ['0', '0', '1', '1', '0', '1'], ...]

    def get_table_data(self):
        """Returns the table data, as produced by generate_table_data().
        """
        return self.table_data


class TruthTableGraphic(QTableWidget):
    """The widget used as the table to be displayed.
    """

    def __init__(self, table_data):
        """
        Constructor

        __init__(list<list<str>>)
        """

        # Inherit from QTableWidget.
        super().__init__()
        self.table_data = table_data
        # Make the table read-only.
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setRowCount(len(self.table_data)-1)
        self.setColumnCount(len(self.table_data[0]))
        self.setHorizontalHeaderLabels(self.table_data[0])
        # Table styling - not yet working.
        # stylesheet = "QHeaderView::section{" \
        #              "background-color:Whitesmoke;" \
        #              "}"
        # self.setStyleSheet(stylesheet)

        # Fill out the rest of the table with truth values.
        for i in range(1, len(self.table_data)):
            for j in range(len(self.table_data[i])):
                item = QTableWidgetItem(self.table_data[i][j])
                # Centre.
                item.setTextAlignment(132)
                # Add table item to table.
                self.setItem(i-1, j, item)

        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        # self.resize(self.sizeHint())
        # self.setFixedSize(self.horizontalHeader().length() + 40,
        #                   self.verticalHeader().length() + 50)


class TruthTableWindow(QMainWindow):
    """The window that displays the truth table.
    """

    def __init__(self, table_data):
        """
        Constructor

        __init__(list<list<str>>)
        """

        # Inherit from QMainWindow.
        super().__init__()
        main_layout = QGridLayout()
        truth_table_graphic = TruthTableGraphic(table_data)
        # window_width = truth_table_graphic.width()
        # window_height = truth_table_graphic.height()
        main_layout.addWidget(truth_table_graphic, 0, 0)
        main_widget = QWidget()
        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)
        # Place this window slightly offset from the starting position of the
        # main window.
        self.setGeometry(80, 110, 425, 540)
        self.setWindowTitle("Logicheck - Truth Table")
        self.setWindowIcon(QIcon("LogicheckIcon3.png"))
