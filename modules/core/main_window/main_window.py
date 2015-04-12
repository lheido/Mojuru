#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QAction

from alter import Alter

@Alter.alter('mojuru_set_main_window')
def set_main_window(app):
    app.main_window = MainWindow()
    app.main_window.show()

class MainWindow(QMainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('Mojuru')
        label = QLabel('Test Module Main Window', self)
        self.setCentralWidget(label)
        