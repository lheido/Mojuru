#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt
from PyQt5.Qsci import QsciLexerPython
from PyQt5.Qsci import QsciLexerBash
from PyQt5.Qsci import QsciLexerCMake
from PyQt5.Qsci import QsciLexerCPP
from PyQt5.Qsci import QsciLexerCSharp
from PyQt5.Qsci import QsciLexerIDL
from PyQt5.Qsci import QsciLexerJava
from PyQt5.Qsci import QsciLexerJavaScript
from PyQt5.Qsci import QsciLexerCSS
from PyQt5.Qsci import QsciLexerD
from PyQt5.Qsci import QsciLexerDiff
from PyQt5.Qsci import QsciLexerFortran
from PyQt5.Qsci import QsciLexerHTML
from PyQt5.Qsci import QsciLexerXML
from PyQt5.Qsci import QsciLexerLua
from PyQt5.Qsci import QsciLexerMakefile
from PyQt5.Qsci import QsciLexerMatlab
from PyQt5.Qsci import QsciLexerPascal
from PyQt5.Qsci import QsciLexerPerl
from PyQt5.Qsci import QsciLexerPostScript
from PyQt5.Qsci import QsciLexerPOV
from PyQt5.Qsci import QsciLexerRuby
from PyQt5.Qsci import QsciLexerSpice
from PyQt5.Qsci import QsciLexerSQL
from PyQt5.Qsci import QsciLexerTCL
from PyQt5.Qsci import QsciLexerTeX
from PyQt5.Qsci import QsciLexerVerilog
from PyQt5.Qsci import QsciLexerVHDL
from PyQt5.Qsci import QsciLexerYAML

from alter import ModuleManager


class EditorHelper:

    language_helper = {
        "Python": (
            QsciLexerPython,
            ["py"],
            {
                'comment_line': '#'
            }
        ), 
        "CPP": (
            QsciLexerCPP, 
            ["c","cpp","h"],
            {
                'comment_line': '//'
            }
        ),
        "HTML": (
            QsciLexerHTML, 
            ["html","php", "module", "inc"],
            {
                'comment_line': '<!-- %content% -->'
            }
        ), 
        "CSS": (
            QsciLexerCSS,
            ["css", "scss"],
            {
                'comment_line': '/* %content% */'
            }
        ),
        "Ruby": (
            QsciLexerRuby,
            ["rb"],
            {
                'comment_line': '//'
            }
            
        ), 
        "SQL": (
            QsciLexerSQL, 
            ["sql"],
            {
                'comment_line': '--'
            }
        ),
        "Perl": (
            QsciLexerPerl,
            ["pl","pm","perl","agi","pod"],
            {
                'comment_line': '//'
            }
        ), 
        "JavaScript": (
            QsciLexerJavaScript,
            ["js", "json"],
            {
                'comment_line': '//'
            }
        ),
        "Lua": (
            QsciLexerLua,
            ["lua"],
            {
                'comment_line': '//'
            }
        ), 
        "Bash": (
            QsciLexerBash,
            ["sh","zsh","tcsh","ksh","ash","configure"],
            {
                'comment_line': '#'
            }
        ), 
        "D": (
            QsciLexerD,
            ["d","di"],
            {
                'comment_line': '//'
            }
        ),
        "Java": (
            QsciLexerJava,
            ["java","jsp"],
            {
                'comment_line': '//'
            }
        ), 
        "Makefile": (
            QsciLexerMakefile,
            ["makefile","MakeFile","Makefile","mk","mak","GNUmakefile"],
            {
                'comment_line': '#'
            }
        ),
        "TCL": (
            QsciLexerTCL,
            ["tcl","tk","wish"],
            {
                'comment_line': '//'
            }
        ), 
        "VHDL": (
            QsciLexerVHDL,
            ["vhd","vhdl"],
            {
                'comment_line': '//'
            }
        ),
        "Verilog": (
            QsciLexerVerilog,
            ["v"],
            {
                'comment_line': '//'
            }
        ),
        "XML": (
            QsciLexerXML,
            ["xml","sgml","xsl","xslt","xsd","xhtml"],
            {
                'comment_line': '<!-- %content% -->'
            }
        ), 
        "YAML": (
            QsciLexerYAML,
            ["yaml","yml"],
            {
                'comment_line': '#'
            }
        ),
        "Diff": (
            QsciLexerDiff,
            ["diff","patch","rej"],
            {
                'comment_line': '//'
            }
        ), 
        "TeX": (
            QsciLexerTeX,
            ["tex","sty","idx","ltx","latex"],
            {
                'comment_line': '//'
            }
        ), 
        "CMake": (
            QsciLexerCMake,
            ["cmake","ctest"],
            {
                'comment_line': '//'
            }
        ), 
        "Matlab": (
            QsciLexerMatlab,
            ["m"],
            {
                'comment_line': '//'
            }
        )
    }
    
    SETTINGS_AUTO_CLOSE_BRACKETS = 'editor/editor_helper_auto_close_brackets'
    SETTINGS_USE_TABS_TO_INDENT = 'editor/editor_helper_use_tabs_to_indent'
    
    @classmethod
    def lang_from_file_info(cls, file_info):
        suffix = file_info.suffix()
        for language, info in cls.language_helper.items():
            if suffix in info[1]:
                return language
        return None
    
    @classmethod
    def language_lexer(cls, file_info):
        suffix = file_info.suffix()
        for language, info in cls.language_helper.items():
            if suffix in info[1]:
                return cls.language_helper[language][0]
        return None
    
    @classmethod
    def auto_close_brackets_quotes(cls, editor_widget, action):
        ModuleManager.core['settings'].Settings.set_value(
            cls.SETTINGS_AUTO_CLOSE_BRACKETS,
            action.isChecked()
        )
    
    @classmethod
    def brakets_quotes_array(cls):
        #return [
        #    Qt.Key_QuoteDbl, Qt.Key_Apostrophe, Qt.Key_BraceLeft, 
        #    Qt.Key_ParenLeft
        #]
        return {
            "'": "'", 
            '"': '"', 
            "(": ")", 
            "{": "}",
            "[": "]"
        }
    
    @classmethod
    def use_tabs_to_indent(cls, editor_widget, action):
        ModuleManager.core['settings'].Settings.set_value(
            cls.SETTINGS_USE_TABS_TO_INDENT,
            action.isChecked()
        )
        editor_widget.editor.setIndentationsUseTabs(action.isChecked())
