#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import pkg_resources
import html

from PyQt5.QtCore import Qt, QUrl, pyqtSignal
from PyQt5.QtWidgets import QAction, QDialog, QVBoxLayout
from PyQt5.QtWebKitWidgets import QWebView, QWebInspector
from PyQt5.QtWebKit import QWebSettings

from alter import Alter
from alter import ModuleManager
from .editor_helper import EditorHelper


@Alter.alter('tab_widget_add_tab')
def open_file(tab_widget, file_info):
    tab_widget.add_tab(AceEditor, file_info, True)


class AceEditor(QWebView):
    """ Embbeded Ace javascript web editor """
    
    is_ready = pyqtSignal()
    
    def __init__(self, file_info, parent=None):
        super(AceEditor, self).__init__(parent)
        self.parent = parent
        self.file_info = file_info
        self.language = EditorHelper.lang_from_file_info(file_info)
        self.is_ready.connect(self.editor_ready)
        self.main_frame().javaScriptWindowObjectCleared.connect(self.__self_js)
        pckg, file_name = 'ace_editor', 'ace_editor.html'
        resource = pkg_resources.resource_string(pckg, file_name)
        html_template = str(resource, 'utf-8')
        #insert file content
        with open(self.file_info.absoluteFilePath(), 'r') as f:
            text = f.read()
            if self.language == 'HTML':
                text = html.escape(text)
            html_template = html_template.replace('{{ content }}', text)
        base_url = QUrl.fromLocalFile(os.path.dirname(__file__))
        self.setHtml(html_template, base_url)
        self.configure()
    
    def main_frame(self):
        """ Convinient function to get main QWebFrame """
        return self.page().mainFrame()
    
    def send_js(self, script):
        """ Convinient function to send javascript to ace editor """
        self.main_frame().evaluateJavaScript(script)

    
    def __self_js(self):
        self.main_frame().addToJavaScriptWindowObject('AceEditor', self)
    
    def editor_ready(self):
        if self.language != None:
            mode = 'editor.getSession().setMode("ace/mode/{0}");'
            self.send_js(mode.format(self.language.lower()))
    
    def configure(self):
        settings = self.settings()
        settings.setAttribute(QWebSettings.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebSettings.DeveloperExtrasEnabled, True)
        
        self.inspector = QWebInspector(self)
        showInspectorAction = QAction('showInspector', self)
        showInspectorAction.triggered.connect(self.showInspector)
        self.addAction(showInspectorAction)
    
    def showInspector(self):
        self.dialogInspector = QDialog(self)
        self.dialogInspector.setLayout(QVBoxLayout())
        self.dialogInspector.layout().addWidget(self.inspector)
        self.dialogInspector.setModal(False)
        self.dialogInspector.show()
        
