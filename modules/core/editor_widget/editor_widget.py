#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTextCodec
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QStatusBar

from .editor import Editor


class EditorWidget(QWidget):
    
    def __init__(self, file_info, parent=None):
        super(EditorWidget, self).__init__(parent)
        
        self.v_box = QVBoxLayout(self)
        self.v_box.setSpacing(0)
        self.v_box.setContentsMargins(0, 0, 0, 0)
        
        self.editor = Editor(file_info, self)
        self.editor.modificationChanged[bool].connect(
            self.on_modification_changed)
        
        self.status_bar = QStatusBar(self)
        self.status_bar.setSizeGripEnabled(False)
        
        self.v_box.addWidget(self.editor)
        self.v_box.addWidget(self.status_bar)
        
        self.setLayout(self.v_box)
        
        self.permanent_widget = QWidget(self.status_bar)
        self.h_box = QHBoxLayout(self.permanent_widget)
        self.h_box.setSpacing(0)
        self.h_box.setContentsMargins(0, 0, 0, 0)
        self.permanent_widget.setLayout(self.h_box)
        
        self.menu_button = QPushButton('Menu', self.permanent_widget)
        self.menu_button.clicked.connect(self.on_menu_button_clicked)
        self.h_box.addWidget(self.menu_button)
        
        self.status_bar.addPermanentWidget(self.permanent_widget)
        
        self.menu = QMenu(self)
        self.add_action(self.tr('Save'), 'ctrl+s', self.editor.save)
    
    def on_modification_changed(self, modified):
        pass
    
    def on_menu_button_clicked(self):
        pos = self.status_bar.mapToGlobal(self.permanent_widget.pos())
        menu_size = self.menu.sizeHint()
        menu_height = menu_size.height()
        menu_width = menu_size.width()
        pos.setY(pos.y() - menu_height)
        pos.setX(pos.x() - menu_width + self.permanent_widget.width())
        if len(self.menu.actions()) > 0:
            self.menu.exec(pos)
    
    def add_action(self, name, shortcut, callback, icon = None):
        """
        Ajoute une action au context menu et au widget navigation lui même.
        Créer une fonction à la volé pour fournir des arguments aux fonctions
        associé aux actions.
        """
        action = QAction(name, self)
        if icon:
            action.setIcon(icon)
        action.setShortcut(shortcut)
        action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        action.triggered.connect(self.__wrapper(callback))
        self.addAction(action)
        self.menu.addAction(action)
        
    def add_separator(self):
        """Simple abstraction of self.context_menu.addSeparator()"""
        self.menu.addSeparator()

    def __wrapper(self, callback):
        def __new_function():
            """
            __new_function représente la forme de tous les callbacks connecté
            à une action pour pouvoir utiliser les raccourcis en même temps que
            le menu contextuel.
            """
            callback(self)
        return __new_function