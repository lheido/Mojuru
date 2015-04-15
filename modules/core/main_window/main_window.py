#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QSplitter

from alter import Alter

@Alter.alter('mojuru_set_main_window')
def set_main_window(app):
    app.main_window = MainWindow()
    app.main_window.show()

class MainWindow(QMainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('Mojuru')
        
        self.populate_central_widget()
    
    def populate_central_widget(self):
        self.vertical_splitter = QSplitter(Qt.Vertical, self)
        self.vertical_widgets = []
        
        self.horizontal_splitter = QSplitter(
            Qt.Horizontal, self.vertical_splitter)
        self.horizontal_widgets = []
        self.vertical_widgets.append(self.horizontal_splitter)
        
        Alter.invoke_all(
            'main_window_add_vertical_widget',
            self.vertical_widgets,
            self
        )
        for widget in self.vertical_widgets:
            self.vertical_splitter.addWidget(widget)
        
        Alter.invoke_all(
            'main_window_add_horizontal_widget',
            self.horizontal_widgets,
            self.vertical_splitter
        )
        for widget in self.horizontal_widgets:
            self.horizontal_splitter.addWidget(widget)
        
        self.setCentralWidget(self.vertical_splitter)