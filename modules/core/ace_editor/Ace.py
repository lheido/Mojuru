#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import pkg_resources
import html

from PyQt5.QtCore import Qt, QUrl, pyqtSignal
from PyQt5.QtWidgets import QAction, QDialog, QVBoxLayout, QSizePolicy
from PyQt5.QtWebKitWidgets import QWebView, QWebInspector
from PyQt5.QtWebKit import QWebSettings

from alter import Alter
from alter import ModuleManager
from .editor_helper import EditorHelper

class Ace(QWebView):
    """ Embbeded Ace javascript web editor """
    
    isReady = pyqtSignal()
    modificationChanged = pyqtSignal(bool)
    cursorPositionChanged = pyqtSignal(int, int)
    
    def __init__(self, file_info, parent=None):
        super(Ace, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.parent = parent
        self.file_info = file_info
        self.language = EditorHelper.lang_from_file_info(file_info)
        
        settings = self.settings()
        settings.setAttribute(QWebSettings.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebSettings.DeveloperExtrasEnabled, True)
        self.inspector = QWebInspector(self)
        showInspectorAction = QAction('showInspector', self)
        showInspectorAction.triggered.connect(self.showInspector)
        self.addAction(showInspectorAction)
        
        self.isReady.connect(self.editor_ready)
        self.modificationChanged.connect(self.modification_changed)
        self.main_frame().javaScriptWindowObjectCleared.connect(self.__self_js)
        pckg, file_name = 'ace_editor', 'ace_editor.html'
        resource = pkg_resources.resource_string(pckg, file_name)
        html_template = str(resource, 'utf-8')
        #insert file content
        with open(self.file_info.absoluteFilePath(), 'r') as f:
            text = f.read()
            text = html.escape(text)
            html_template = html_template.replace('{{ content }}', text)
        base_url = QUrl.fromLocalFile(os.path.dirname(__file__))
        self.setHtml(html_template, base_url)
        self.modified = False
    
    def modification_changed(self, b):
        self.modified = b
    
    def save(self, parent, action=None):
        Alter.invoke_all('editor_presave', self)
        if self.modified:
            with open(self.file_info.absoluteFilePath(), 'w') as f:
                f.write(self.get_value())
            self.modificationChanged.emit(False)
            parent.status_bar.showMessage(self.tr("Saved file."))
            Alter.invoke_all('editor_save', self)
        else :
            parent.status_bar.showMessage(self.tr("Nothing to save."))
    
    def main_frame(self):
        """ Convinient function to get main QWebFrame """
        return self.page().mainFrame()
    
    def send_js(self, script):
        """ Convinient function to send javascript to ace editor """
        return self.main_frame().evaluateJavaScript(script)

    def __self_js(self):
        self.main_frame().addToJavaScriptWindowObject('AceEditor', self)
    
    def editor_ready(self):
        if self.language != None:
            mode = 'editor.getSession().setMode("ace/mode/{0}");'
            self.send_js(mode.format(self.language.lower()))
        self.send_js('editor.focus()')
    
    def showInspector(self):
        self.dialogInspector = QDialog(self)
        self.dialogInspector.setLayout(QVBoxLayout())
        self.dialogInspector.layout().addWidget(self.inspector)
        self.dialogInspector.setModal(False)
        self.dialogInspector.show()
    
    def get_value(self):
        return self.send_js('editor.getValue()')
    
    def set_value(self, content):
        self.send_js('editor.setValue("{0}")'.format(content))
    
    def insert(self, text):
        self.send_js('editor.insert("{0}")'.format(text))
    
    def set_mode(self, language):
        cmd = 'editor.getSession().setMode("ace/mode/{0}")'
        self.send_js(cmd.format(language))
    
    def set_theme(self, theme):
        self.send_js('editor.setTheme("ace/theme/{0}")'.format(theme))
    
    def get_selected_text(self):
        cmd = 'editor.session.getTextRange(editor.getSelectionRange())'
        return self.send_js(cmd)
    
    def get_cursor(self):
        cmd = 'editor.selection.getCursor()'
        return self.send_js(cmd)
    
    def got_to_line(self, line):
        cmd = 'editor.gotoLine({0})'
        self.send_js(cmd.format(line))
    
    def get_length(self):
        return self.send_js('editor.session.getLength()');
    
    def set_tab_size(self, tab_size):
        self.send_js('editor.getSession().setTabSize({0})'.format(tab_size))
    
    def set_use_soft_tabs(self, b):
        self.send_js('editor.getSession().setUseSoftTabs({0})'.format(b))
    
    def set_font_size(self, font_size):
        cmd = "document.getElementById('editor').style.fontSize='{0}px'"
        self.send_js(cmd.format(font_size))
    
    def set_use_wrap_mode(self, b):
        cmd = "editor.getSession().setUseWrapMode({0})"
        self.send_js(cmd.format(b))
    
    def set_highlight_active_line(self, b):
        cmd = "editor.setHighlightActiveLine({0})"
        self.send_js(cmd.format(b))
    
    def set_show_print_margin(self, b):
        cmd = "editor.setShowPrintMargin({0})"
        self.send_js(cmd.format(b))
    
    def set_read_only(self, b):
        self.send_js('editor.setReadOnly({0})'.format(b))
    
