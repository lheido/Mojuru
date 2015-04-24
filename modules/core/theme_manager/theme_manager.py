#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import importlib
import json
import pkg_resources

from PyQt5.QtCore import QFileInfo
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QActionGroup

from alter import Alter
from alter import ModuleManager

sys.path.append(QFileInfo('themes').absoluteFilePath())

@Alter.alter('mojuru_init')
def on_app_start(application):
    ThemeManager.set_active_style_sheet(application)

@Alter.alter('main_window_init')
def on_main_window_start(main_window):
    main_window.theme_menu = main_window.menuBar().addMenu(
        main_window.tr('Themes'))
    themes_directory = QFileInfo('themes')
    if themes_directory.exists():
        active_theme = ThemeManager.get_active_theme()
        path = themes_directory.absoluteFilePath()
        group_action = QActionGroup(main_window)
        group_action.setExclusive(True)
        for theme in os.listdir(path):
            action = QAction(theme, main_window)
            action.setData(theme)
            action.setCheckable(True)
            if theme == active_theme:
                action.setChecked(True)
            action.changed.connect(ThemeManager.wrapper(main_window))
            group_action.addAction(action)
            group_action.addAction(action)
            main_window.theme_menu.addAction(action)
    


class ThemeManager:
    
    KEY_ACTIVE_THEME = 'theme/active_theme'
    
    @classmethod
    def get_active_theme(cls):
        return ModuleManager.core['settings'].Settings.value(
            cls.KEY_ACTIVE_THEME, 'default_dark')
    
    @classmethod
    def set_active_style_sheet(cls, application):
        theme_name = cls.get_active_theme()
        theme = ModuleTheme(theme_name)
        application.setStyleSheet(theme.style_sheet)
    
    @classmethod
    def save_active_theme(cls, theme):
        ModuleManager.core['settings'].Settings.set_value(
            cls.KEY_ACTIVE_THEME, theme)
    
    @classmethod
    def wrapper(cls, main_window):
        def on_changed():
            current_action = main_window.sender()
            theme = ModuleTheme(current_action.data())
            if current_action.isChecked():
                main_window.setStyleSheet(theme.style_sheet)
                cls.save_active_theme(theme.name)
                #for each other action, set checked to false
                for action in main_window.theme_menu.actions():
                    if action.data() != theme.name:
                        action.setChecked(False)
        return on_changed


class ModuleTheme:
    
    style_sheet = ''
    editor_theme = {}
    
    def __init__(self, theme_name):
        self.name = theme_name
        self.style_sheet = self.get_resource_string('theme.css')
        self.editor_theme = self.get_resource_json('editor.json')
    
    def get_resource_string(self, file_name):
        resource = pkg_resources.resource_string(self.name, file_name)
        return str(resource, 'utf-8')
    
    def get_resource_json(self, file_name):
        resource = ''
        try:
            resource = self.get_resource_string(file_name)
        except FileNotFoundError:
            return {}
        if resource != '':
            return json.loads(resource)
        return {}