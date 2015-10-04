#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QFileInfo
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QKeySequence
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QTreeView
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QAction

from alter import Alter
from alter import ModuleManager

from .model import File, Class, Function
from .file_inspector_helper import FileInspectorHelper

TabWidget = ModuleManager.core['tab_widget'].TabWidget

@Alter.alter('main_window_add_horizontal_widget')
def add_horizontal_widget(horizontal_widgets, parent):
    horizontal_widgets["file_inspector"] = FileInspector(parent)

@Alter.alter('main_window_connect_widgets')
def connect_widgets(vertical_widgets, horizontal_widgets):
    getattr(horizontal_widgets['navigation'], 'onFileItemActivated').connect(
        getattr(horizontal_widgets['file_inspector'], 'onFileItemActivated'))
    getattr(horizontal_widgets['tab_widget'], 'currentChangedFileInfo').connect(
        getattr(horizontal_widgets['file_inspector'], 'onFileItemActivated'))

class FileInspector(QTreeView):
    """docstring for FileInspector"""
    
    def __init__(self, parent=None):
        super(FileInspector, self).__init__(parent)
        self.model = QStandardItemModel(self)
        self.setModel(self.model)
        self.file_info = None
        header = QStandardItem('')
        self.model.setHorizontalHeaderItem(0, header)
    
    def populate(self, file_info=None):
        if file_info is not None and file_info.fileName() != self.model.horizontalHeaderItem(0).text():
            self.file_info = file_info
            self.model.clear()
            file_path = file_info.absoluteFilePath()
            try:
                db_file = FileInspectorHelper.query(File).filter(
                    File.path == file_path).one()
            except Exception as e:
                db_file = FileInspectorHelper.insert_file(file_info, True)
            if db_file:
                for classe in db_file.classes:
                    parent = QStandardItem(classe.name)
                    for method in classe.methods:
                        parent.appendRow(QStandardItem(method.name))
                    self.model.appendRow(parent)
                for function in db_file.functions:
                    self.model.appendRow(QStandardItem(function.name))
            header = QStandardItem(file_info.fileName())
            self.model.setHorizontalHeaderItem(0, header)
            self.expandAll()
    
    @pyqtSlot(QFileInfo)
    def onFileItemActivated(self, file_info):
        self.populate(file_info)
    
