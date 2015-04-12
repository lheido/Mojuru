#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QWidget, QAction
from PyQt5.QtCore import Qt, pyqtSlot, QFileInfo

from navigation import Navigation

class Label(QLabel):
    
    def __init__(self, text, parent=None):
        super(Label, self).__init__(text, parent)
    
    # the function name must be equal to signal name.
    # decorator because reduce the amount of memory used and is slightly faster
    @pyqtSlot(QFileInfo)
    def onFileItemActivated(self, qFileInfo):
        print('multiple connect test')

if __name__ == '__main__':
    import sys
    
    app = QApplication(sys.argv)
    
    hbox = QHBoxLayout()
    navigation = Navigation()
    label = Label('Test pyqtSlot 1')
    label2 = Label('Test pyqtSlot 2')
    getattr(navigation, 'onFileItemActivated').connect(
        getattr(label, 'onFileItemActivated'))
    getattr(navigation, 'onFileItemActivated').connect(
        getattr(label2, 'onFileItemActivated'))
#    navigation.onFileItemActivated.connect(label.onFileItemActivated)
    hbox.addWidget(navigation)
    hbox.addWidget(label)
    hbox.addWidget(label2)
    
    widget = QWidget()
    widget.setLayout(hbox)
    widget.show()
    
    app.exec_()