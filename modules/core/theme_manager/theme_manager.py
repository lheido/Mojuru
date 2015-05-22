#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import importlib
import json
import pkg_resources

from PyQt5.QtCore import QFileInfo
from PyQt5.QtGui import QColor
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
            

@Alter.alter('editor_configure')
def configure(editor):
    ThemeManager.set_editor_theme_base16(
        editor, 
        editor.lang_lexer if hasattr(editor, 'lang_lexer') else None
    )
    

class ThemeManager:
    
    KEY_ACTIVE_THEME = 'theme/active_theme'
    
    @classmethod
    def get_resource_string(cls, package, file_name):
        resource = pkg_resources.resource_string(package, file_name)
        return str(resource, 'utf-8')
    
    @classmethod
    def get_resource_json(cls, package, file_name):
        resource = ''
        try:
            resource = cls.get_resource_string(package, file_name)
        except FileNotFoundError:
            return None
        if resource != '':
            return json.loads(resource)
        return False
    
    @classmethod
    def get_active_theme(cls):
        return ModuleManager.core['settings'].Settings.value(
            cls.KEY_ACTIVE_THEME, 'default_dark')
    
    @classmethod
    def set_active_style_sheet(cls, application):
        theme_name = cls.get_active_theme()
        theme = cls.get_resource_string(theme_name, 'theme.css')
        application.setStyleSheet(theme)
    
    @classmethod
    def set_editor_theme(cls, editor, lexer):
        theme_name = cls.get_active_theme()
        theme = ModuleTheme(theme_name)
        for elt, value in theme.editor_theme.items():
            color = QColor(value) if value[0] == '#' else None
            if elt == 'MarginsBackground' and color:
                editor.setMarginsBackgroundColor(color)
            elif elt == 'MarginsForeground' and color:
                editor.setMarginsForegroundColor(color)
            elif elt == 'FoldMargin' and color:
                editor.setFoldMarginColors(color, color)
            elif elt == 'CaretLineBackground' and color:
                editor.setCaretLineBackgroundColor(color)
            elif elt == 'CaretForeground' and color:
                editor.setCaretForegroundColor(color)
            elif elt == 'Paper' and color:
                lexer.setPaper(color) if lexer else editor.setPaper(color)
            elif elt == 'MatchedBraceBackgroundColor' and color:
                editor.setMatchedBraceBackgroundColor(color)
            elif elt == 'MatchedBraceForegroundColor' and color:
                editor.setMatchedBraceForegroundColor(color)
            elif elt == 'UnmatchedBraceBackgroundColor' and color:
                editor.setUnmatchedBraceBackgroundColor(color)
            elif elt == 'UnmatchedBraceForegroundColor' and color:
                editor.setUnmatchedBraceForegroundColor(color)
            elif elt == 'SelectionBackgroundColor' and color:
                editor.setSelectionBackgroundColor(color)
            elif elt == 'SelectionForegroundColor' and color:
                editor.setSelectionForegroundColor(color)
            if lexer:
                if elt == 'DefaultPaper' and color:
                    lexer.setDefaultPaper(color)
                elif 'KeywordsEnsemble' in elt:
                    if editor.lang in elt:
                        lexer.keys_ens = value
                        def wrapper():
                            def keywords(ens):
                                return lexer.keys_ens[ens]
                            return keywords
                        setattr(lexer, 'keywords', wrapper())
                elif hasattr(lexer, elt) and color:
                    lexer.setColor(color, getattr(lexer, elt))
            if not lexer and elt == 'Default' and color:
                editor.setColor(color)
    
    @classmethod
    def set_editor_theme_base16(cls, editor, lexer):
        """
        Get active theme and set up editor and lexer theme.
        """
        theme_name = ModuleManager.core['settings'].Settings.value(
            'editor/active_syntax_theme', 'mojuru.dark')
        theme = cls.get_resource_json('editor_widget',
            'base16-builder/output/mojuru/base16-{0}.json'.format(theme_name))
        if theme:
            #set up default lexer theme
            if lexer:
                to_lexer = theme['settings']['lexer']
                if editor.lang in theme:
                    to_lexer.update(theme[editor.lang])
                cls.set_colors(to_lexer, lexer, cls.lexer_callback)
                editor.setLexer(lexer)
            #set up default editor theme
            to_editor = theme['settings']['editor']
            cls.set_colors(to_editor, editor, cls.editor_callback)
            
    
    @classmethod
    def set_colors(cls, items_dict, obj, callback):
        """
        items_dict may be like this: '<method>': {'color': '<color_value>'}.
        See base16 generated theme.
        obj is the obj to set up the color|attribute (lexer or editor)
        callback is a function to define how <method> is set
        See example with editor_callback|lexer_callback function below
        """
        for method, value in items_dict.items():
            color_value = value['color'] if 'color' in value else None
            if color_value and color_value[0] == '#':
                color = QColor(color_value)
                callback(obj, method, value, color)
            else:
                callback(obj, method, value, None)
    
    @classmethod
    def editor_callback(cls, obj, method, value, color):
        if color and hasattr(obj, 'set'+method):
            getattr(obj, 'set'+method)(color)
        elif 'foreground' in value and 'background' in value:
            fore = QColor(value['foreground']) 
            back = QColor(value['background'])
            getattr(obj, 'set'+method)(fore, back)
    
    @classmethod
    def lexer_callback(cls, obj, method, value, color):
        if value and method == 'KeywordsEnsemble':
            for i, ens in enumerate(value):
                obj.keys_ens[i] = ens
        elif color and (method == 'Paper' or method == 'DefaultPaper'):
            getattr(obj, 'set'+method)(color)
        else:
            obj.setColor(color, getattr(obj, method))
    
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