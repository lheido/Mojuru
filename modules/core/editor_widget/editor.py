#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTextCodec
from PyQt5.Qsci import QsciScintilla

from .editor_helper import EditorHelper


class Editor(QsciScintilla):
    """
    Editor based on QsciScintilla.
    """
    def __init__(self, file_info, parent=None):
        super(Editor, self).__init__(parent)
        self.file_info = file_info
        self.setUtf8(True)
        with open(file_info.absoluteFilePath(), 'r') as f:
            text = f.read()
            self.setText(text)
            self.setModified(False)
        lexer_class = EditorHelper.language_lexer(file_info)
        if lexer_class:
            self.setLexer(lexer_class())
        self.modificationChanged[bool].connect(self.on_modification_changed)
    
    def on_modification_changed(self, modified):
        pass
    
    def save(self, parent):
        if self.isModified():
            with open(self.file_info.absoluteFilePath(), 'w') as f:
                #I don't understand encoding >< but it works
                b_text = self.text().encode('utf-8')
                f.write(str(b_text, 'utf-8'))
            self.setModified(False)
        else :
            parent.status_bar.showMessage(self.tr("Nothing to save."))