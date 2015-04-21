#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
# Here, you might want to set the ``QT_API`` to use.
# Valid values are: 'pyqt5', 'pyqt4' or 'pyside'
# See 
# import os; os.environ['QT_API'] = 'pyside'
from pyqode.core import api
from pyqode.core import modes
from pyqode.core import panels
from pyqode.qt import QtWidgets


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # create editor and window
    window = QtWidgets.QMainWindow()
    editor = api.CodeEdit()
    window.setCentralWidget(editor)

    # start the backend as soon as possible
    editor.backend.start('server.py')

    # append some modes and panels
    editor.modes.append(modes.CodeCompletionMode())
    editor.modes.append(modes.PygmentsSyntaxHighlighter(editor.document()))
    editor.modes.append(modes.CaretLineHighlighterMode())
    editor.panels.append(panels.SearchAndReplacePanel(),
                         api.Panel.Position.BOTTOM)
    # change color scheme
    editor.modes.get(modes.PygmentsSyntaxHighlighter).pygments_style = 'monokai'
    # change action shortcut
    editor.action_duplicate_line.setShortcut('Ctrl+Shift+Down')
    # open a file
    editor.file.open(__file__)

    # run
    window.show()
    app.exec_()