#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import shutil

from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QFileInfo

class FileSystemHelper:
    
    file_to_copy = None
    file_to_cut = None
    
    def __init__(self):
        raise Exception('')
    
    @classmethod
    def rename(cls, file_info, parent):
        model_index = parent.model.index(file_info.absoluteFilePath())
        parent.model.openPersistentEditor(model_index)
    
    @classmethod
    def copy(cls, file_info, parent):
        cls.file_to_copy = file_info
        cls.file_to_cut = None
    
    @classmethod
    def cut(cls, file_info, parent):
        cls.file_to_cut = file_info
        cls.file_to_copy = None
    
    @classmethod
    def paste(cls, file_info, parent):
        dst = file_info.absoluteDir().absolutePath()
        if file_info.isDir():
            dst = file_info.absoluteFilePath()
        if cls.file_to_copy:
            shutil.copy2(cls.file_to_copy.absoluteFilePath(), dst)
        if cls.file_to_cut:
            shutil.move(cls.file_to_cut.absoluteFilePath(), dst)
        cls.file_to_copy = None
        cls.file_to_cut = None
    
    @classmethod
    def delete(cls, file_info, parent):
        path = file_info.absoluteFilePath()
        if file_info.isFile():
            reply = parent.question('Delete this file', 'Are you sure?')
            if reply == QMessageBox.Yes:
                index = parent.model.index(path)
                parent.model.remove(index)
        elif file_info.isDir():
            reply = parent.question('Delete this directory', 'Are you sure?')
            if reply == QMessageBox.Yes:
                index = parent.model.index(path)
                parent.model.rmdir(index)
    
    @classmethod
    def new_file(cls, file_info, parent):
        dst = file_info.absoluteDir().absolutePath()
        if file_info.isDir():
            dst = file_info.absoluteFilePath()
        file_name = QFileDialog.getSaveFileName(parent, 'New file', dst)[0]
        if file_name:
            with open(file_name, 'x') as fout:
                fout.write('')
    
    @classmethod
    def new_directory(cls, file_info, parent):
        dst = file_info.absoluteDir().absolutePath()
        if file_info.isDir():
            dst = file_info.absoluteFilePath()
        file_name = QFileDialog.getSaveFileName(parent, 'New directory', dst)[0]
        if file_name:
            name = QFileInfo(file_name).fileName()
            parent_index = parent.model.index(dst)
            parent.model.mkdir(parent_index, name)
    
    @classmethod
    def ready(cls):
        return cls.file_to_copy != None or cls.file_to_cut != None
    
    @classmethod
    def ready_file_fame(cls):
        if cls.file_to_copy: return cls.file_to_copy.baseName()
        if cls.file_to_cut : return cls.file_to_cut.baseName()