#!/usr/bin/env python

"""
argument.py

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

from copy import deepcopy
from itertools import product
from more_itertools import unique_everseen
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QFont
from truth_table import TruthTable, TruthTableWindow

# Unicode for logical operators
operators1 = [u'\u00ac', u'\u2227', u'\u2228', u'\u2262', u'\u2261', u'\u2283']
operators = [u'\u00ac', u'\u2227', u'\u2228', u'\u2a01', u'\u21d4', u'\u21d2']
# html (prefix "&#", postfix ";"): 172, 8743, 8744, 10753, 8660, 8658


def is_symbol(c):
    if c.isalpha() or c.isdigit():
        return True
    else:
        return False


class PropArg(object):
    """Stores and determines the validity of propositional arguments.
    """

    def __init__(self, arg):
        """
        Constructor
        """

        # list of premises/expressions, and conclusion if provided
        self._arg = arg
        # e.g. self._arg = ['Sv((P^Q)->R)', '-S', 'Q']
        self._pin = [c for p in arg for c in p if is_symbol(c)]
        # number of propositions in argument
        self.n = len(self._pin)

    def evaluate(self, test=True):
        """If test == True, states if a propositional argument is valid or
        invalid. If invalid, counter examples are listed in output.

        If test == False, only calculate the truth values of the input.

        is_valid(int, list<str>) -> str
        Precondition: arg is in the correct format.
        """

        bad_vals = []
        valid = True
        all_truth = []

        # generate list of all unique proposition symbols contained in arg
        psyms = list(unique_everseen(self._pin))
        # e.g. psyms = ['S', '5', '1', 'R']
        n = len(psyms)
        # create all permutations of 0's and 1's of length n,
        # i.e. every possible set of truth values
        perm = [x for x in product('01', repeat=n)]

        for i in range(len(perm)):
            vals = {psyms[j]: int(perm[i][j]) for j in range(0, n)}
            # E.g. vals = {'S':0, '5':1 '1':0, 'R':1} - assigns truth values
            # in perm to propositions.
            arg = self.convert(psyms, vals)
            # determine truth value of arguments based on truth values in vals
            truth = [self.det(premise) for premise in arg]
            if -1 in truth:
                return -1
            all_truth.append(truth)
            if test and truth[-1] == 0 and truth[:-1] == (len(arg) - 1) * [1]:
                valid = False
                # construct list of counter examples for output
                bad_vals.append(vals)
            else:
                continue

        self.truth_table = TruthTable(deepcopy(psyms),
                                      deepcopy(self._arg),
                                      deepcopy(perm),
                                      deepcopy(all_truth), conc=test)
        self._table_data = self.truth_table.get_table_data()

        if test:
            if valid:
                output = '\nThe argument is valid.\n'
            else:
                output = '\nThe argument is invalid. Counter examples:\n'
                for v in bad_vals:
                    output += '\n'
                    for k in psyms:
                        output += str(k) + ' = ' + str(v[k]) + '  '
                    output += '\n'
                output += '\n'
            return output

        return

    def convert(self, psyms, vals):
        """Converts the propositions (denoted as letters or numbers) in psyms
        to their corresponding truth values from vals.

        convert(list<str>, dict) -> list<str>
        """
        # e.g. psyms = ['S', '0', '1', 'R']
        #      vals = {'S':0, '0':1 '1':0, 'R':1}
        # Error to be fixed: using '1' or '0' as a symbol
        # e.g. psyms = ['a', '0']
        #      vals = {'a':0, '0':1}
        #      a's have already been replaced with '0' - these 0's then get
        #      replaced with 1's on the second iteration
        argx = []
        for premise in self._arg:
            for c in psyms:
                premise = premise.replace(c, str(vals[c]))
            argx.append(premise)
        return argx
        # e.g. argx = ['0->((1^0)v1)', '~0', '0']

    def det(self, premise):
        """Determines the truth value of premise based on proposition
        truth values in vals

        det(str, dict) -> int)
        """

        q = 0
        while premise.find('(') != -1:
            # Loop while a bracket is found, i.e. there is a nested argument.
            # Find the location of the first set of brackets.
            openb = premise.find('(')
            close = premise.find(')')
            while premise.count('(', openb + 1, close) != \
                    premise.count(')', openb + 1, close):
                # Check the number of open brackets is not equal to
                # the number of close brackets between the current
                # open bracket and the current close bracket.
                # If so, change close point to correct close bracket.
                close = premise.find(')', close + 1)
            # replace old premise with truth value of nested arg
            premise = premise.replace(premise[openb:close + 1],
                                      str(self.det(premise[openb + 1:close])))

        digits = [c for c in premise if c.isdigit()]
        op = premise.strip(''.join(digits))
        props = [int(c) for c in digits]
        p = props[0]
        if len(props) > 1:
            q = props[1]

        # Perform logical operation according to operator.
        if op == '':  # no operator - leave as is
            v = p
        elif op == operators[0]:  # NOT
            v = int(not p)
        elif op == operators[1]:  # AND
            v = (p and q)
        elif op == operators[2]:  # OR
            v = (p or q)
        elif op == operators[3]:  # XOR
            v = int(p != q)
        elif op == operators[4]:  # IFF
            v = int(p == q)
        elif op == operators[5]:  # IF
            v = int(not (p == 1 and q == 0))
        else:
            return -1  # Something went wrong - unhandled exception
        return v

    def get_table_data(self):
        return self._table_data


class ArgCheck(QWidget):

    def __init__(self, main_window):
        """
        Constructor
        """

        # inherit
        super().__init__()
        self.parent = main_window
        self._arg = []
        self._post_conc = False
        self.raw_premises = []
        self.pretty_premises = []
        self._abort = False
        self.current_premise = None
        self.premise_labels = []

        font1 = QFont()
        font1.setPointSize(11)
        self.setFont(font1)

        # create input layout
        self.prompt_label = QLabel("Expression:")
        self.entry_line = QLineEdit()
        self.entry_line.setFont(font1)
        self.input_layout = QGridLayout()
        self.input_layout.setAlignment(Qt.AlignTop)
        self.input_layout.addWidget(self.prompt_label, 0, 0)
        self.input_layout.addWidget(self.entry_line, 0, 1)
        self.input_layout.addWidget(QLabel("Commands:"), 1, 0)
        self.input_layout.addWidget(QLabel("Operators:"), 2, 0)

        # create command layout
        commands = ["&Add", "&Conclude", "Cl&ear", "&Back", "&Reset"]
        command_methods = [self.add_prem, self.add_conc, self.clear_entry,
                           self.undo_prem, self.trans_reset(True)]
        command_tooltips = ["Add a premise", "Add the conclusion",
                            "Clear the entry line", "Remove last premise",
                            "Remove current argument"]
        self.command_layout = QHBoxLayout()
        for name, method, tooltip in zip(commands, command_methods,
                                         command_tooltips):
            btn = QPushButton(name)
            btn.clicked.connect(method)
            btn.setToolTip(tooltip)
            width = btn.fontMetrics().boundingRect(name).width() + 20
            btn.setMaximumWidth(width)
            self.command_layout.addWidget(btn)
        self.command_layout.addStretch(1)
        self.input_layout.addLayout(self.command_layout, 1, 1)

        # create ops layout
        self.op_layout = QHBoxLayout()
        self.op_tooltips = ["Negation/NOT (F1)", "Conjunction/AND (F2)",
                            "Inclusive disjunction/OR (F3)",
                            "Exclusive disjunction/XOR (F4)",
                            "Biconditional/IFF (F5)", "Conditional/IF (F6)"]
        for op, tooltip in zip(operators, self.op_tooltips):
            btn = QPushButton(op)
            btn.clicked.connect(self.add_op)
            btn.setToolTip(tooltip)
            btn.setFont(font1)
            width = btn.fontMetrics().boundingRect(op).width() + 20
            btn.setMaximumWidth(width)
            self.op_layout.addWidget(btn)
        self.op_layout.addStretch(1)
        self.input_layout.addLayout(self.op_layout, 2, 1)

        # .connect(QShortcut(QKeySequence("Alt+N"), self),
        #              QtCore.SIGNAL("activated()"), self._not)

        # create arg layout
        self.arg_layout = QVBoxLayout()
        self.arg_layout.setAlignment(Qt.AlignTop)
        self.arg_widget = QWidget()
        self.arg_widget.setLayout(self.arg_layout)
        # stylesheet1 = "background-color:White"
        # self.arg_widget.setStyleSheet(stylesheet1)

        # scroll area properties
        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.arg_widget)
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.addWidget(self.scroll)

        # create truth table viewer layout
        self.tableBtn = QPushButton("Show &truth table")
        self.tableBtn.setMaximumWidth(125)
        self.tableBtn.clicked.connect(self.show_truth_table)
        self.tableBtn.setDisabled(True)
        self.table_layout = QHBoxLayout()
        self.table_layout.addWidget(self.tableBtn, alignment=Qt.AlignCenter)

        # create main layout
        layouts = [self.input_layout, self.command_layout, self.op_layout,
                   self.scroll_layout, self.table_layout]
        positions = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)]
        self.main_layout = QGridLayout()
        for layout, pos in zip(layouts, positions):
            self.main_layout.addLayout(layout, pos[0], pos[1])
        self.setLayout(self.main_layout)

    def trans_reset(self, clear):
        return lambda: self.reset(clear)

    @staticmethod
    def check_premise(premise):
        # This function takes a brute-force approach to handling as many kinds
        # of syntax errors as possible and giving a helpful description to the
        # user of what is wrong.
        # E.g. premise = '0?((1?0)?1)'
        result = 0
        all_brackets = False
        op_indices = []

        if premise == '':  # handled in add_prem
            return result

        if '0' in premise or '1' in premise:
            return "Syntax error: cannot use 0 or 1 as a symbol"

        if len(premise) == 1:
            if is_symbol(premise):
                return result
            else:
                return "Syntax error: invalid symbol(s) - must be " \
                       "alphanumeric"

        if premise[0] == ')':
            return "Syntax error: input starts with a closed bracket"
        if is_symbol(premise[0]):
            if premise[1] == '(' or premise[1] == ')':
                return "Syntax error: bracket immediately follows" \
                         " first character"
        elif premise[0] != '(':
            return "Syntax error: input starts with an operator"

        if len(premise) == 2:
            return "Syntax error: input cannot be 2 characters long"

        if premise[0] == '(':
            all_brackets = True

        if premise.count('(') != premise.count(')'):
            return "Syntax error: brackets do not close"

        if not is_symbol(premise[-1]) and premise[-1] not in operators and \
            premise[-1] != "(" and premise[-1] != ")":
            return "Syntax error: invalid symbol(s) - must be " \
                   "alphanumeric"

        for i in range(1, len(premise)-1):

            if is_symbol(premise[i]):  # symbol
                all_brackets = False
                if is_symbol(premise[i-1]) or is_symbol(premise[i+1]):
                    result = "Syntax error: proposition(s) represented" \
                           " by multiple symbols"
                    break

                if premise[i-1] == ')' or premise[i+1] == '(':
                    result = "Syntax error: incorrect bracket use"
                    break
                elif premise[i-1] == '(' and premise[i+1] == ')':
                    result = "Syntax error: incorrect bracket use"
                    break

            else:  # not a symbol

                if premise[i] == '(' and premise[i-1] == ')':  # bracket
                    result = "Syntax error: consecutive brackets"
                    break
                elif premise[i] == ')' and premise[i-1] == '(':
                    result = "Syntax error: consecutive brackets"
                    break
                elif premise[i] == ')' and is_symbol(premise[i+1]):
                    result = "Syntax error: symbol immediately follows close" \
                             " bracket"
                    break

                elif premise[i] != '(' and premise[i] != ')':  # operator
                    if premise[i] not in operators:
                        result = "Syntax error: invalid symbol(s) - must be " \
                                 "alphanumeric"
                        break
                    op_indices.append(i)
                    if i-1 in op_indices:
                        result = "Syntax error: adjacent operators"
                        break
                    if i-2 in op_indices and premise[i] != operators[0]:
                        result = "Syntax error: sub-expression needs brackets"
                    all_brackets = False
                    if premise[i] == operators[0]:  # negation
                        if premise[i-1] != '(' or premise[i+1] == ')':
                            result = "Syntax error: incorrect bracket position"
                            break
                        elif premise[i+1] != '(' and premise[i+2] != ')':
                            # open bracket on left, symbol or op on right
                            result = "Syntax error: negation needs brackets"
                            break

                    else:  # other operator
                        if premise[i-1] == '(' or premise[i+1] == ')':
                            result = "Syntax error: incorrect bracket position"
                            break
                        elif is_symbol(premise[i-1]) == False \
                                and is_symbol(premise[i+1]) == False\
                                and premise[i-1] != ')'\
                                and premise[i+1] != '(':
                            result = "Syntax error: no symbol next to" \
                                     " operator"
                            break

        if all_brackets:
            result = "Syntax error: input contains only brackets"

        return result

    def return_entry(self):
        self.entry_line.setFocus()

    def clear_entry(self):
        self.entry_line.clear()
        self.entry_line.setFocus()

    def add_prem(self, is_conc=False):
        self._abort = False

        self.parent.statusBar().clearMessage()

        premise = self.entry_line.text()
        error = self.check_premise(premise.replace(" ", ""))
        if error != 0:
            self.parent.statusBar().showMessage(error)
            self._abort = True
            self.return_entry()
            return

        if is_conc:
            if premise == '':
                self.parent.statusBar().showMessage("Enter an expression to "
                                                    "conclude with")
                self._abort = True
                self.return_entry()
            else:
                self.raw_premises.append(premise)
                pretty_premise = premise
                self.pretty_premises.append(pretty_premise) 
            # elif premise == '':  # handles late conclude
            #     premise = self._arg[-1]
            #     self.clear_layout(self.arg_layout)
            #     for e in self.pretty_premises[:-1]:
            #         self.arg_layout.addWidget(QLabel(e))
                pretty_premise = '____\n\n' + u'\u2234' + \
                                 ' ' + premise
                self.current_premise = QLabel(pretty_premise)
                self.arg_layout.addWidget(self.current_premise)
                self.premise_labels.append(self.current_premise)
                premise = premise.replace(' ', '')
                self._arg.append(premise)
                self.tableBtn.setDisabled(False)

        else:
            if premise != '':  # if something is entered
                if self._post_conc:  # checks for a new argument
                    self.reset()
                    self._post_conc = False
                self.raw_premises.append(premise)
                pretty_premise = "".join([str(len(self._arg) + 1), ". ",
                                          premise])
                self.pretty_premises.append(pretty_premise)
                self.current_premise = QLabel(pretty_premise)
                self.arg_layout.addWidget(self.current_premise)
                self.premise_labels.append(self.current_premise)
                premise = premise.replace(' ', '')
                self._arg.append(premise)  # add premise to overall argument
                self.tableBtn.setDisabled(False)

        self.clear_entry()

    def undo_prem(self):
        # This is the function mapped to the "Back" button. It is a specific
        # "undo" button that removes the latest addition to the display box
        # and returns the input to the entry box.
        # We can only remove a previously added premise if at least one is
        # already there.
        if self._arg:  # and not self._post_conc:
            # In the case of only one premise being there, we must disable
            # the truth table button for when the display is empty.
            if len(self._arg) == 1:
                self.tableBtn.setDisabled(True)
            # If the user just concluded an argument:
            if self._post_conc:
                # Delete the conclusion-specific output.
                self.outputLabel.deleteLater()
                # Go back to pre-conclusion state.
                self._post_conc = False
            # Delete the most recently added premise from display.
            self.premise_labels[-1].deleteLater()
            # Remove this from the list of displayed premises.
            self.premise_labels.remove(self.premise_labels[-1])
            # Clear entry box in preparation for returned premise.
            self.clear_entry()
            # Insert removed premise.
            self.entry_line.insert(self.raw_premises[-1])
            # Bring the focus to the entry box.
            self.return_entry()
            # Remove the raw premise text from the list.
            self.raw_premises.remove(self.raw_premises[-1])
            # Remove the processed premise text from the list.
            self._arg.remove(self._arg[-1])
            # Remove the displayed premise text from the list.
            self.pretty_premises.remove(self.pretty_premises[-1])

    def add_conc(self):
        if self._arg and not self._post_conc:
            if len(self._arg) == 1 and self.entry_line.text() == "":
                self.parent.statusBar().showMessage("Argument must have at "
                                                    "least one premise and "
                                                    "one conclusion")
                self.return_entry()
                return
            self.add_prem(is_conc=True)
            if self._abort:
                return
            self.prop_arg = PropArg(self._arg)
            output = self.prop_arg.evaluate()
            if output == -1:  # Unhandled exception
                self.parent.statusBar().showMessage("An unknown error "
                                                    "occurred. Check for"
                                                    " ambiguity in the"
                                                    " expression.")
                # Force "Back" button
                self.undo_prem()
                return
            self.outputLabel = QLabel(output)
            self.arg_layout.addWidget(self.outputLabel)
            self._post_conc = True

        else:
            # self.reset()
            self.parent.statusBar().showMessage("Add a premise first")
            self.return_entry()

    def show_truth_table(self):
        if not self._post_conc:
            self.prop_arg = PropArg(self._arg)
            self.prop_arg.evaluate(test=False)
        self.table_data = self.prop_arg.get_table_data()
        self.table_window = TruthTableWindow(self.table_data)
        self.table_window.show()

    @staticmethod
    def layout_widgets(layout):
        return (layout.itemAt(i) for i in range(layout.count()))

    @staticmethod
    def clear_layout(layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                clearLayout(child.layout())

    def reset(self, clear=False):
        if clear:
            self.clear_entry()
        self._arg = []
        self.raw_premises = []
        self.pretty_premises = []
        self.premise_labels = []
        self.clear_layout(self.arg_layout)
        self.parent.statusBar().showMessage("")
        self.tableBtn.setDisabled(True)

    def add_op(self):
        self.entry_line.insert(self.sender().text())
        self.return_entry()

    def show_op_info(self):
        pass

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_F1:
            self.entry_line.insert(operators[0])
        elif e.key() == Qt.Key_F2:
            self.entry_line.insert(operators[1])
        elif e.key() == Qt.Key_F3:
            self.entry_line.insert(operators[2])
        elif e.key() == Qt.Key_F4:
            self.entry_line.insert(operators[3])
        elif e.key() == Qt.Key_F5:
            self.entry_line.insert(operators[4])
        elif e.key() == Qt.Key_F6:
            self.entry_line.insert(operators[5])

# ERROR LOG:
    # Conclusion formatting is dodgy.
