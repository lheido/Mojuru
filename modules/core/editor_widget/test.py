#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt, QFileInfo
from PyQt5.QtWidgets import QApplication

from editor_widget import EditorWidget

if __name__ == '__main__':
    import sys
    
    app = QApplication(sys.argv)
    
    file_info = QFileInfo(
        '/home/lheido/Dropbox/pythonLibs/modules/editor_widget/editor.py'
    )
    editor = EditorWidget(file_info)
    editor.show()
    
    app.exec_()