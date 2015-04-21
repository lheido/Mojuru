#!/usr/bin/python3
# -*- coding: utf-8 -*-

import collections

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QSize
from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QSplitter

from alter import Alter
from alter import ModuleManager

@Alter.alter('mojuru_set_main_window')
def set_main_window(app):
    app.main_window = MainWindow()
    app.main_window.show()

class MainWindow(QMainWindow):
    
    KEY_WINDOW_SIZE = 'main_window/size'
    KEY_WINDOW_MAXIMIZED = 'main_window/maximized'
    KEY_WINDOW_POSITION = 'main_window/position'
    KEY_H_SPLITTER_STATE = 'main_window/h_splitter_state'
    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('Mojuru')
        
        action = QAction('Reload MainWindow', self)
        action.setShortcut('ctrl+shift+alt+r')
        action.triggered.connect(self.reload_central_widget)
        self.addAction(action)
        
        quit_action = QAction('Quit', self)
        quit_action.setShortcut('ctrl+q')
        quit_action.triggered.connect(self.on_quit)
        self.addAction(quit_action)
        
        self.vertical_splitter = QSplitter(Qt.Vertical, self)
        self.setCentralWidget(self.vertical_splitter)
        self.load_central_widget()
        
        size = ModuleManager.core['settings'].Settings.value(
            self.KEY_WINDOW_SIZE, QSize(600, 400))
        maximized = ModuleManager.core['settings'].Settings.value(
            self.KEY_WINDOW_MAXIMIZED, False)
        position = ModuleManager.core['settings'].Settings.value(
            self.KEY_WINDOW_POSITION, QPoint(0,0))
        if maximized == 'true':
            self.showMaximized()
        else:
            self.resize(size)
            self.move(position)
    
    def closeEvent(self, event):
        self.on_quit()
    
    def save_state(self):
        ModuleManager.core['settings'].Settings.set_value(
            self.KEY_WINDOW_SIZE, self.size())
        ModuleManager.core['settings'].Settings.set_value(
            self.KEY_WINDOW_MAXIMIZED, self.isMaximized())
        ModuleManager.core['settings'].Settings.set_value(
            self.KEY_WINDOW_POSITION, self.pos())
        ModuleManager.core['settings'].Settings.set_value(
            self.KEY_H_SPLITTER_STATE, self.horizontal_splitter.saveState())
    
    def on_quit(self):
        self.save_state()
        self.close()
    
    def load_central_widget(self):
        self.populate_central_widget()
        self.connect_widgets()
    
    def populate_central_widget(self):
        self.vertical_widgets = collections.OrderedDict()
        
        self.horizontal_splitter = QSplitter(
            Qt.Horizontal, self.vertical_splitter)
        self.horizontal_widgets = collections.OrderedDict()
        self.vertical_widgets["horizontal_splitter"] = self.horizontal_splitter
        
        Alter.invoke_all(
            'main_window_add_vertical_widget',
            self.vertical_widgets,
            self
        )
        for widget in self.vertical_widgets.values():
            self.vertical_splitter.addWidget(widget)
        
        Alter.invoke_all(
            'main_window_add_horizontal_widget',
            self.horizontal_widgets,
            self.vertical_splitter
        )
        for widget in self.horizontal_widgets.values():
            self.horizontal_splitter.addWidget(widget)
        
        #restore horizontal splitter state
        state = ModuleManager.core['settings'].Settings.value(
            self.KEY_H_SPLITTER_STATE,
            None
        )
        if state:
            self.horizontal_splitter.restoreState(state)
    
    def connect_widgets(self):
        Alter.invoke_all(
            'main_window_connect_widgets', 
            self.vertical_widgets, 
            self.horizontal_widgets
        )
    
    def reload_central_widget(self):
        self.save_state()
        for index in range(self.vertical_splitter.count()):
            widget = self.vertical_splitter.widget(index)
            widget.hide()
            widget.setParent(None)
            del widget
        Alter.clear()
        ModuleManager.reload_all_modules('core')
        ModuleManager.reload_all_modules('custom')
        self.load_central_widget()