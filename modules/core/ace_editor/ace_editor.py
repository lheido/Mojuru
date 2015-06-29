#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import pkg_resources
import html

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTextCodec
from PyQt5.QtGui import QKeySequence
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QStatusBar
from PyQt5.QtWidgets import QLabel

from alter import Alter
from alter import ModuleManager
from .editor_helper import EditorHelper
from .Ace import Ace


@Alter.alter('tab_widget_add_tab')
def open_file(tab_widget, file_info):
    tab_widget.add_tab(AceEditor, file_info)


class AceEditor(QWidget):
    """ Embbeded Ace javascript web editor """
    
    
    def __init__(self, file_info, parent=None):
        super(AceEditor, self).__init__(parent)
        self.parent = parent
        self.file_info = file_info
        self.language = EditorHelper.lang_from_file_info(file_info)
        
        self.status_bar = StatusBar(self)
        
        self.editor = Ace(self.file_info)
        self.editor.modificationChanged[bool].connect(
            self.on_modification_changed)
        self.editor.cursorPositionChanged.connect(self.on_cursor_changed)
        
        self.v_box = QVBoxLayout(self)
        self.v_box.setSpacing(0)
        self.v_box.setContentsMargins(0, 0, 0, 0)
        
        self.v_box.addWidget(self.editor)
        self.v_box.addWidget(self.status_bar)
        
        self.setLayout(self.v_box)
        
        self.status_bar.menu_button.clicked.connect(
            self.on_menu_button_clicked)
        
        self.menu = QMenu(self)
        self.add_action(self.tr('Save'), 'ctrl+s', self.editor.save)
        self.add_separator()
        
        self.setFocusPolicy(Qt.NoFocus)
        self.setFocusProxy(self.editor)
        
        Alter.invoke_all('editor_widget_init', self)
    
    def on_modification_changed(self, modified):
        if self.parent:
            self.parent.on_current_modified(modified)
    
    def on_cursor_changed(self, line, index):
        self.status_bar.showMessage(
            self.tr("Line {0}, column {1}".format(line + 1, index))
        )
    
    def on_menu_button_clicked(self):
        pos = self.status_bar.mapToGlobal(self.status_bar.menu_button.pos())
        menu_size = self.menu.sizeHint()
        menu_height = menu_size.height()
        menu_width = menu_size.width()
        pos.setY(pos.y() - menu_height)
        pos.setX(pos.x() - menu_width + self.status_bar.menu_button.width())
        if len(self.menu.actions()) > 0:
            self.menu.exec(pos)
    
    def add_action(self, name, shortcut, callback, **kwargs):
        """
        Ajoute une action au context menu et au widget navigation lui même.
        Créer une fonction à la volé pour fournir des arguments aux fonctions
        associé aux actions.
        """
        action = QAction(name, self)
        if 'icon' in kwargs:
            action.setIcon(kwargs['icon'])
        if 'checkable' in kwargs and kwargs['checkable']:
            action.setCheckable(True)
            if 'checked' in kwargs:
                checked = True if kwargs['checked'] == 'true' else False
                action.setChecked(
                    checked
                )
        
        action.setShortcut(shortcut)
        action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        
        if 'wrapped' in kwargs and kwargs['wrapped'] is False:
            action.triggered.connect(callback)
        else:
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
            action = self.sender()
            callback(self, action)
        return __new_function

class StatusBar(QWidget):
    
    def __init__(self, parent=None):
        super(StatusBar, self).__init__(parent)
        self.label = QLabel('', self)
        self.menu_button = QPushButton('', self)
        self.menu_button.setIcon(QIcon('images/properties.png'))
        self.menu_button.setFlat(True)
        self.h_box = QHBoxLayout(self)
        self.h_box.setSpacing(0)
        self.h_box.addWidget(self.label)
        self.h_box.addWidget(self.menu_button, 1, Qt.AlignRight)
        self.setLayout(self.h_box)
    
    def showMessage(self, message=''):
        self.label.setText(message)