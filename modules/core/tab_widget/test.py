#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QTextEdit, QAction

from tab_widget import TabWidget

class TextEdit(QTextEdit):
    
    def __init__(self, i,parent=None):
        super(TextEdit, self).__init__(parent)
        
        action = QAction('test', self)
        action.setShortcut('ctrl+d')
        action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        action.triggered.connect(lambda : print('test', i))
        self.addAction(action)

if __name__ == '__main__':
    import sys
    
    app = QApplication(sys.argv)
    
    
    tab_widget = TabWidget()
    tab_widget.addTab(TextEdit(1), 'Onglet Test 1')
    tab_widget.addTab(TextEdit(2), 'Onglet Test 2')
    tab_widget.addTab(TextEdit(3), 'Onglet Test 3')
    tab_widget.show()
    
    app.exec_()