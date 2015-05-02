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
            ["py"]
        ), 
        "CPP": (
            QsciLexerCPP, 
            ["c","cpp","h"]
        ),
        "HTML": (
            QsciLexerHTML, 
            ["html","php", "module", "inc"]
        ), 
        "CSS": (
            QsciLexerCSS,
            ["css"]
        ),
        "Ruby": (
            QsciLexerRuby,
            ["rb"]
        ), 
        "SQL": (
            QsciLexerSQL, 
            ["sql"]
        ),
        "Perl": (
            QsciLexerPerl,
            ["pl","pm","perl","agi","pod"]
        ), 
        "JavaScript": (
            QsciLexerJavaScript,
            ["js", "json"]
        ),
        "Lua": (
            QsciLexerLua,
            ["lua"]
        ), 
        "Bash": (
            QsciLexerBash,
            ["sh","zsh","tcsh","ksh","ash","configure"]
        ), 
        "D": (
            QsciLexerD,
            ["d","di"]
        ),
        "Java": (
            QsciLexerJava,
            ["java","jsp"]
        ), 
        "Makefile": (
            QsciLexerMakefile,
            ["makefile","MakeFile","Makefile","mk","mak","GNUmakefile"]
        ),
        "TCL": (
            QsciLexerTCL,
            ["tcl","tk","wish"]
        ), 
        "VHDL": (
            QsciLexerVHDL,
            ["vhd","vhdl"]
        ),
        "Verilog": (
            QsciLexerVerilog,
            ["v"]
        ),
        "XML": (
            QsciLexerXML,
            ["xml","sgml","xsl","xslt","xsd","xhtml"]
        ), 
        "YAML": (
            QsciLexerYAML,
            ["yaml","yml"]
        ),
        "Diff": (
            QsciLexerDiff,
            ["diff","patch","rej"]
        ), 
        "TeX": (
            QsciLexerTeX,
            ["tex","sty","idx","ltx","latex"]
        ), 
        "CMake": (
            QsciLexerCMake,
            ["cmake","ctest"]
        ), 
        "Matlab": (
            QsciLexerMatlab,
            ["m"]
        )
    }
    
    SETTINGS_AUTO_CLOSE_BRACKETS = 'editor_helper_auto_close_brackets'
    
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
