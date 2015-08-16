#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Navigation projects core module.
"""

import os.path
import collections

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QFileInfo
from PyQt5.QtCore import QDir
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QTreeView
from PyQt5.QtWidgets import QFileSystemModel
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QMessageBox

from alter import Alter
from alter import ModuleManager
from .file_system_helper import FileSystemHelper

@Alter.alter('main_window_add_horizontal_widget')
def add_horizontal_widget(horizontal_widgets, parent):
    horizontal_widgets['navigation'] = Navigation(parent)
    policy = horizontal_widgets["navigation"].sizePolicy()
    policy.setHorizontalStretch(1)
    horizontal_widgets["navigation"].setSizePolicy(policy)


class Navigation(QWidget):
    """
    Navigation class definition.
    
    Provide a combobox to switch on each opened directories and display it into
    a tree view
    
    Provide 2 useful function (to use in alter module):
      - add_action(name, shortcut, callback)
         - callback take 2 arguments : file_info and parent
      - add_separator()
    
    """
    
    SETTINGS_DIRECTORIES = 'navigation_dirs'
    SETTINGS_CURRENT_DIR = 'navigation_current_dir'
    
    onFileItemActivated = pyqtSignal(QFileInfo, name="onFileItemActivated")
    onDirItemActivated = pyqtSignal(QFileInfo, name="onDirItemActivated")
    
    def __init__(self, parent=None):
        super(Navigation, self).__init__(parent)
        self.setObjectName("Navigation")
        
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)
        
        self.menu_button = QPushButton('Select directory', self)
        self.menu_button.setFlat(True)
#        self.menu_button.clicked.connect(self.on_menu_button_clicked)
        self.menu = QMenu(self)
        self.menu_button.setMenu(self.menu)
        self.menu_directories = QMenu(self)
        self.menu_directories.setTitle('Directories')
        self.menu_add_action(
            'Open directory', self.open_directory, None, QKeySequence.Open)
        self.menu_add_separator()
        self.menu_add_action('Refresh', self.reset, None, QKeySequence.Refresh)
        # @TODO invoke_all
        self.menu_add_separator()
        self.menu.addMenu(self.menu_directories)
        
        self.tree = QTreeView(self)
        self.model = FileSystemModel(self)
        self.tree.setModel(self.model)
        self.tree.setColumnHidden(1, True)
        self.tree.setColumnHidden(2, True)
        self.tree.setColumnHidden(3, True)
        self.tree.setHeaderHidden(True)
        # only to expand directory or activated with one click
        self.tree.clicked.connect(self.on_item_clicked)
        # else, for file use activated signal
        self.tree.activated.connect(self.on_item_activated)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.on_context_menu)
        
        self.widgets = collections.OrderedDict()
        self.widgets['menu_button'] = self.menu_button
        self.widgets['tree'] = self.tree
        
        # @ToDo: Alter.invoke_all('add_widget', self.widgets)
        
        for name, widget in self.widgets.items():
            if name == 'menu_button':
                self.layout.addWidget(widget, 0, Qt.AlignLeft)
            else:
                self.layout.addWidget(widget)
        
        self.context_menu = QMenu(self)
        self.add_action('New file', QKeySequence.New, 
                        FileSystemHelper.new_file)
        self.add_separator()
        self.add_action('Copy', QKeySequence.Copy, FileSystemHelper.copy)
        self.add_action('Cut', QKeySequence.Cut, FileSystemHelper.cut)
        self.add_action('Paste', QKeySequence.Paste, FileSystemHelper.paste)
        self.add_separator()
        self.add_action('Delete', QKeySequence.Delete, 
                        FileSystemHelper.delete)
        
        # @ToDo Alter.invoke_all('navigation_add_action', self)
        
        #restore previous session and data
        dirs = ModuleManager.core['settings'].Settings.value(
            self.SETTINGS_DIRECTORIES, None, True)
        for directory_path in dirs:
            name = os.path.basename(directory_path)
            self.menu_add_directory(name, directory_path)
        current_dir = ModuleManager.core['settings'].Settings.value(
            self.SETTINGS_CURRENT_DIR, '')
        if current_dir:
            for action in self.menu_directories.actions():
                if action.data() == current_dir:
                    action.trigger()
        
        self.menu_button.setFocusPolicy(Qt.NoFocus)
        self.menu_button.setFocusProxy(self.tree)
    
    def reset(self, file_info):
        self.model.beginResetModel()
        current_dir = ModuleManager.core['settings'].Settings.value(
            self.SETTINGS_CURRENT_DIR, '')
        if current_dir:
            for action in self.menu_directories.actions():
                if action.data() == current_dir:
                    action.trigger()
    
    def on_menu_button_clicked(self):
        pos = self.mapToGlobal(self.menu_button.pos())
        menu_width = self.menu.sizeHint().width()
        pos.setY(pos.y() + self.menu_button.height())
#        pos.setX(pos.x() + self.menu_button.width() - menu_width)
        if len(self.menu.actions()) > 0:
            self.menu.exec(pos)
    
    def menu_add_action(self, name, callback, data=None, shortcut=None, icon=None):
        action = QAction(name, self)
        if icon:
            action.setIcon(icon)
        if shortcut:
            action.setShortcut(shortcut)
            action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        if data:
            action.setData(data)
        action.triggered.connect(callback)
        self.addAction(action)
        self.menu.addAction(action)
    
    def menu_add_directory(self, name, data):
        action = QAction(name, self)
        action.setData(data)
        action.triggered.connect(self.on_menu_action_triggered)
        self.menu_directories.addAction(action)
        return action
    
    def menu_add_separator(self):
        self.menu.addSeparator()
    
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
        self.context_menu.addAction(action)
    
    def add_separator(self):
        """Simple abstraction of self.context_menu.addSeparator()"""
        self.context_menu.addSeparator()
    
    def __wrapper(self, callback):
        def __new_function():
            """
            __new_function représente la forme de tous les callbacks connecté
            à une action pour pouvoir utiliser les raccourcis en même temps que
            le menu contextuel.
            """
            action = self.sender()
            file_info = action.data()
            if not file_info:
                indexes = self.tree.selectedIndexes()
                if indexes:
                    model_index = indexes[0]
                    file_info = self.model.fileInfo(model_index)
                    callback(file_info, self)
                elif action.shortcut() == QKeySequence.New:
                    file_info = self.model.fileInfo(self.tree.rootIndex())
                    callback(file_info, self)
            else:
                callback(file_info, self)
                action.setData(None)
        return __new_function
    
    def question(self, text, informative_text = None):
        message_box = QMessageBox(self)
        message_box.setText(text)
        if informative_text:
            message_box.setInformativeText(informative_text)
        message_box.setStandardButtons(
            QMessageBox.No | QMessageBox.Yes)
        message_box.setDefaultButton(QMessageBox.No)
        return message_box.exec()
    
    def on_context_menu(self, point):
        model_index = self.tree.indexAt(point)
        file_info = self.model.fileInfo(model_index)
        # pour chaque action on met a jour les data (file_info)
        # puis on altère les actions (ex enabled)
        for action in self.context_menu.actions():
            if not action.isSeparator():
                action.setData(file_info)
                action.setEnabled(model_index.isValid())
                if action.shortcut() == QKeySequence.New:
                    action.setEnabled(True)
                    if not model_index.isValid():
                        file_info = self.model.fileInfo(self.tree.rootIndex())
                        action.setData(file_info)
                if action.shortcut() == QKeySequence.Paste:
                    enable = FileSystemHelper.ready() and model_index.isValid()
                    action.setEnabled(enable)
                if action.shortcut() == QKeySequence.Delete:
                    # remove directory only if is an empty directory
                    if model_index.isValid() and file_info.isDir():
                        path = file_info.absoluteFilePath()
                        # QDir(path).count() always contains '.' and '..'
                        action.setEnabled(QDir(path).count() == 2)
                # @ToDo 
                #Alter.invoke_all(
                #    'navigation_on_menu_action', 
                #    model_index, file_info, action, self)
        if len(self.context_menu.actions()) > 0:
            self.context_menu.exec(self.tree.mapToGlobal(point))
        # reset action data, sinon y a des problèmes dans _new_function
        for action in self.context_menu.actions():
            action.setData(None)
    
    def on_item_activated(self, index):
        qFileInfo = self.model.fileInfo(index)
        if qFileInfo.isDir():
            self.onDirItemActivated.emit(qFileInfo)
        else:
            self.onFileItemActivated.emit(qFileInfo)
    
    def on_item_clicked(self, index):
        qFileInfo = self.model.fileInfo(index)
        if qFileInfo.isDir():
            self.onDirItemActivated.emit(qFileInfo)
            self.tree.setExpanded(index, not self.tree.isExpanded(index))
        else:
            self.onFileItemActivated.emit(qFileInfo)
    
    def open_directory(self):
        path = QFileDialog.getExistingDirectory(self, "Open Directory", ".")
        if path:
            name = os.path.basename(path)
            action = self.menu_add_directory(name, path)
            self.save_directories_path()
            action.trigger()
    
    def on_menu_action_triggered(self):
        action = self.sender()
        path = action.data()
        if path:
            self.model.setRootPath(path)
            self.tree.setRootIndex(self.model.index(path))
            self.menu_button.setText(os.path.basename(path))
            self.save_current_dir(path)
    
    def save_directories_path(self):
        ModuleManager.core['settings'].Settings.set_value(
            self.SETTINGS_DIRECTORIES,
            [action.data() for action in self.menu_directories.actions()]    
        )
    
    def save_current_dir(self, path):
        ModuleManager.core['settings'].Settings.set_value(
            self.SETTINGS_CURRENT_DIR,
            path
        )


class FileSystemModel(QFileSystemModel):
    """docstring for FileSystemModle"""
    
    def __init__(self, parent=None):
        super(FileSystemModel, self).__init__(parent)
    
    def data(self, index, role):
        if role == Qt.DecorationRole:
            return None
        if role == Qt.DisplayRole:
            info = self.fileInfo(index)
            if info.isDir():
                return info.fileName()
        if role == Qt.ForegroundRole:
            info = self.fileInfo(index)
            if info.isDir():
                return QColor('#74A494')
        return super(FileSystemModel, self).data(index, role)