#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import pkg_resources
import html
import re

from PyQt5.QtCore import Qt, QUrl, pyqtSignal, pyqtSlot, QEventLoop
from PyQt5.QtWidgets import QAction, QDialog, QVBoxLayout, QSizePolicy
from PyQt5.QtWebKitWidgets import QWebView, QWebInspector
from PyQt5.QtWebKit import QWebSettings

from alter import Alter
from alter import ModuleManager
from .editor_helper import EditorHelper

class Ace(QWebView):
    """ Embbeded Ace javascript web editor """
    
    regex = re.compile('\W*([a-zA-Z\/\_\.]+)')
    
    isReady = pyqtSignal(name='isReady')
    modificationChanged = pyqtSignal(bool)
    cursorPositionChanged = pyqtSignal(int, int, name='cursorPositionChanged')
    
    def __init__(self, file_info, parent=None):
        super(Ace, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.parent = parent
        self.file_info = file_info
        self.language = EditorHelper.lang_from_file_info(file_info)
        self.waitForReady = False
        self.loop = QEventLoop()
        
        settings = self.settings()
        settings.setAttribute(QWebSettings.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebSettings.DeveloperExtrasEnabled, True)
        self.inspector = QWebInspector(self)
        showInspectorAction = QAction('showInspector', self)
        showInspectorAction.triggered.connect(self.showInspector)
        self.addAction(showInspectorAction)
        
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
        
        if not self.waitForReady:
            self.loop.exec()
    
    @pyqtSlot(int, str, str, name='test', result=str)
    @EditorHelper.json_dumps
    def test(self, col, pr, line):
        prefix = self.regex.findall(line[:col])[-1]
        # m = self.regex.search(line[:col])
        # if m:
        #     prefix = m.groups()
        print(prefix)
        return ['plop', 'cool', 42, {'plop':23}]
    
    def modification_changed(self, b):
        self.modified = b
    
    def save(self, parent, action=None):
        Alter.invoke_all('editor_presave', self)
        if self.modified:
            with open(self.file_info.absoluteFilePath(), 'w') as f:
                f.write(self.get_value())
            self.original_to_current_doc()
            self.modificationChanged.emit(False)
            parent.status_bar.showMessage(self.tr("Saved file."))
            Alter.invoke_all('editor_save', self)
        else :
            parent.status_bar.showMessage(self.tr("Nothing to save."))
    
    def toggle_hidden(self, parent, action=None):
        self.set_show_invisibles(action.isChecked())
    
    def toggle_soft_tabs(self, parent, action=None):
        self.set_use_soft_tabs(action.isChecked())
    
    def main_frame(self):
        """ Convinient function to get main QWebFrame """
        return self.page().mainFrame()
    
    def send_js(self, script):
        """ Convinient function to send javascript to ace editor """
        return self.main_frame().evaluateJavaScript(script)
    
    def __self_js(self):
        self.main_frame().addToJavaScriptWindowObject('AceEditor', self)
    
    @pyqtSlot(name='isReady')
    def editor_ready(self):
        if self.language != None:
            self.set_mode(self.language.lower())
        self.set_focus()
        if self.loop.isRunning():
            self.loop.quit()
        self.waitForReady = True
    
    def showInspector(self):
        self.dialogInspector = QDialog(self)
        self.dialogInspector.setLayout(QVBoxLayout())
        self.dialogInspector.layout().addWidget(self.inspector)
        self.dialogInspector.setModal(False)
        self.dialogInspector.show()
    
    def original_to_current_doc(self):
        self.send_js('editor.orignalToCurrentDoc()')
    
    def get_value(self):
        return self.send_js('editor.getValue()')
    
    def set_value(self, content):
        self.send_js('editor.setValue("{0}")'.format(content))
    
    def set_focus(self):
        self.send_js('editor.focus()')
    
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
    
    def get_tab_size(self):
        return self.send_js('editor.getSession().getTabSize()')
    
    def set_use_soft_tabs(self, b):
        b = 'true' if b else 'false'
        self.send_js('editor.getSession().setUseSoftTabs({0})'.format(b))
    
    def set_font_size(self, font_size):
        cmd = "document.getElementById('editor').style.fontSize='{0}px'"
        self.send_js(cmd.format(font_size))
    
    def set_use_wrap_mode(self, b):
        b = 'true' if b else 'false'
        cmd = "editor.getSession().setUseWrapMode({0})"
        self.send_js(cmd.format(b))
    
    def set_highlight_active_line(self, b):
        b = 'true' if b else 'false'
        cmd = "editor.setHighlightActiveLine({0})"
        self.send_js(cmd.format(b))
    
    def set_show_print_margin(self, b):
        b = 'true' if b else 'false'
        cmd = "editor.setShowPrintMargin({0})"
        self.send_js(cmd.format(b))
    
    def set_read_only(self, b):
        b = 'true' if b else 'false'
        self.send_js('editor.setReadOnly({0})'.format(b))
    
    def set_show_invisibles(self, b):
        b = 'true' if b else 'false'
        self.send_js('editor.setShowInvisibles({0})'.format(b))
    
