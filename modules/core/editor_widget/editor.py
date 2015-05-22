#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QEvent
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import QMenu
from PyQt5.Qsci import QsciScintilla
from PyQt5.Qsci import QsciLexer

from alter import Alter
from alter import ModuleManager
from .editor_helper import EditorHelper


class Editor(QsciScintilla):
    """
    Editor based on QsciScintilla.
    """
    def __init__(self, file_info, parent=None):
        super(Editor, self).__init__(parent)
        self.file_info = file_info
        self.lang = EditorHelper.lang_from_file_info(file_info)
        self.setUtf8(True)
        with open(file_info.absoluteFilePath(), 'r') as f:
            text = f.read()
            self.setText(text)
            self.setModified(False)
        self.modificationChanged[bool].connect(self.on_modification_changed)
        
        Alter.invoke_all('editor_init', self)
        
        self.configure()
        
        #self.context_menu = QMenu(self)
        #self.context_menu.addAction('test')
        #self.context_menu.addAction('plop')
        #self.setContextMenuPolicy(Qt.CustomContextMenu)
        #self.customContextMenuRequested.connect(self.on_context_menu)
    
    #def on_context_menu(self, point):
        #self.context_menu.exec(self.mapToGlobal(point))
    
    def configure(self):
        font = QFont()
        font.setFamily('ubuntu mono')
        font.setFixedPitch(True)
        font.setPointSize(12)
        self.setFont(font)
        lexer_class = EditorHelper.language_lexer(self.file_info)
        if lexer_class:
            base_lexer = lexer_class()
            self.lang_lexer = type(self.lang, (lexer_class,), {
                'keys_ens': [base_lexer.keywords(i) for i in range(10)],
                'keywords': lambda self, ens: self.keys_ens[ens]
            })()
        #self.lang_lexer = lexer_class() if lexer_class else None
        #ModuleManager.core['theme_manager'].ThemeManager.set_editor_theme(
        #    self, self.lang_lexer)
        
        if hasattr(self, 'lang_lexer'):
            self.lang_lexer.setFont(font)
            self.setLexer(self.lang_lexer)
        
        fontmetrics = QFontMetrics(font)
        self.setMarginsFont(font)
        self.setMarginLineNumbers(1, True)
        self.setMarginWidth(1, fontmetrics.width("00000"))
        self.setCaretLineVisible(True)
        self.setIndentationGuides(True)
        self.setIndentationsUseTabs(False)
        self.setIndentationWidth(4)
        self.setTabWidth(4)
        self.setAutoIndent(True)
        self.setBackspaceUnindents(True)
        self.setFolding(QsciScintilla.BoxedTreeFoldStyle)
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        self.setEdgeColumn(79)
        self.setEdgeColor(QColor('#424242'))
        self.setEdgeMode(QsciScintilla.EdgeLine)
        
        Alter.invoke_all('editor_configure', self)
    
    def on_modification_changed(self, modified):
        pass
    
    def save(self, parent, action=None):
        Alter.invoke_all('editor_presave', self)
        if self.isModified():
            with open(self.file_info.absoluteFilePath(), 'w') as f:
                #I don't understand encoding >< but it works
                b_text = self.text().encode('utf-8')
                f.write(str(b_text, 'utf-8'))
            self.setModified(False)
            parent.status_bar.showMessage(self.tr("Saved file."))
            Alter.invoke_all('editor_save', self)
        else :
            parent.status_bar.showMessage(self.tr("Nothing to save."))
    
    def zoom_reset(self, parent, action):
        #zoom to default font size
        self.zoomTo(0)
    
    def unindent_current_line(self, parent, action):
        line, index = self.getCursorPosition()
        self.unindent(line)
    
    def indent_current_line(self, parent, action):
        line, index = self.getCursorPosition()
        self.indent(line)
    
    def on_cursor_changed(self, line, index):
        #parent.status_bar.showMessage(
        #    self.tr("Line {line}, column {index}".format(line, index)))
        pass
    
    def keyPressEvent(self, event):
        line, index = self.getCursorPosition()
        events = [event]
        self.auto_close_event(events, line, index)
        #invoke other modules
        Alter.invoke_all('editor_key_presse_event', self, events, line, index)
        
        for evt in events:
            super(Editor, self).keyPressEvent(evt)
    
    def auto_close_event(self, events, line, index):
        event = events[0]
        auto_close_enabled = ModuleManager.core['settings'].Settings.value(
                EditorHelper.SETTINGS_AUTO_CLOSE_BRACKETS,
                'true'
            )
        brackets_quotes = EditorHelper.brakets_quotes_array()
        if auto_close_enabled == 'true' and event.text() in brackets_quotes:
            #if ControlModifier is pressed add ';' after closed parens/etc...
            modifier = ';' if event.modifiers() == Qt.AltModifier else ''
            if self.hasSelectedText():
                selected_text = self.selectedText()
                text_size = len(selected_text)
                replace_text = "{0}{1}{2}{3}".format(
                    event.text(), 
                    selected_text, 
                    brackets_quotes[event.text()],
                    modifier
                )
                self.replaceSelectedText(replace_text)
                #remove orignal event from events list, we do not want to add
                #the default key pressed.
                events.pop(0)
            else:
                insert_text = "{0}{1}".format(
                    brackets_quotes[event.text()], modifier)
                self.insertAt(insert_text, line, index)
            
        if event.key() == Qt.Key_Backspace:
            at_right, at_left = '', ''
            if len(self.text(line)) > index:
                at_right = self.text(line)[index]
            if index > 0:
                at_left = self.text(line)[index-1]
            if at_left in brackets_quotes:
                if brackets_quotes[at_left] == at_right:
                    self.setSelection(line, index, line, index+1)
                    self.replaceSelectedText('')
