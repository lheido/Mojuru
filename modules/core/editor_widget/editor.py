#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import QMenu
from PyQt5.Qsci import QsciScintilla

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
            lexer = lexer_class()
            ModuleManager.core['theme_manager'].ThemeManager.set_editor_theme(
                self, lexer)
            lexer.setFont(font)
            self.setLexer(lexer)
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
    
    def on_modification_changed(self, modified):
        pass
    
    def save(self, parent):
        if self.isModified():
            with open(self.file_info.absoluteFilePath(), 'w') as f:
                #I don't understand encoding >< but it works
                b_text = self.text().encode('utf-8')
                f.write(str(b_text, 'utf-8'))
            self.setModified(False)
            parent.status_bar.showMessage(self.tr("Saved file."))
        else :
            parent.status_bar.showMessage(self.tr("Nothing to save."))
    
    def zoom_reset(self, parent):
        #zoom to default font size
        self.zoomTo(0)
    
    def on_cursor_changed(self, line, index):
        #parent.status_bar.showMessage(
        #    self.tr("Line {line}, column {index}".format(line, index)))
        pass