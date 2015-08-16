#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import json

from PyQt5.QtCore import Qt

from alter import ModuleManager


class EditorHelper:

    supportedModes = {
        'ABAP':        ["^abap$"],
        'ABC':         ["^abc$"],
        'ActionScript':["^as$"],
        'ADA':         ["^ada$|^adb$"],
        'Apache_Conf': ["^htaccess$|^htgroups$|^htpasswd$|^conf$|^htaccess$|^htgroups$|^htpasswd$"],
        'AsciiDoc':    ["^asciidoc$|^adoc$"],
        'Assembly_x86':["^asm$"],
        'AutoHotKey':  ["^ahk$"],
        'BatchFile':   ["^bat$|^cmd$"],
        'C9Search':    ["^c9search_results$"],
        'C_Cpp':       ["^cpp$|^c$|^cc$|^cxx$|^h$|^hh$|^hpp$"],
        'Cirru':       ["^cirru$|^cr$"],
        'Clojure':     ["^clj$|^cljs$"],
        'Cobol':       ["^CBL$|^COB$"],
        'coffee':      ["^coffee$|^cf$|^cson$|^Cakefile$"],
        'ColdFusion':  ["^cfm$"],
        'CSharp':      ["^cs$"],
        'CSS':         ["^css$"],
        'Curly':       ["^curly$"],
        'D':           ["^d|di$"],
        'Dart':        ["^dart$"],
        'Diff':        ["^diff$|^patch$"],
        'Dockerfile':  ["^Dockerfile$"],
        'Dot':         ["^dot$"],
        'Dummy':       ["^dummy$"],
        'DummySyntax': ["^dummy$"],
        'Eiffel':      ["^e$"],
        'EJS':         ["^ejs$"],
        'Elixir':      ["^ex$|^exs$"],
        'Elm':         ["^elm$"],
        'Erlang':      ["^erl$|^hrl$"],
        'Forth':       ["^frt$|^fs$|^ldr$"],
        'FTL':         ["^ftl$"],
        'Gcode':       ["^gcode$"],
        'Gherkin':     ["^feature$"],
        'Gitignore':   ["^.gitignore$"],
        'Glsl':        ["^glsl$|^frag$|^vert$"],
        'golang':      ["^go$"],
        'Groovy':      ["^groovy$"],
        'HAML':        ["^haml$"],
        'Handlebars':  ["^hbs$|^handlebars$|^tpl$|^mustache$"],
        'Haskell':     ["^hs$"],
        'haXe':        ["^hx$"],
        'HTML':        ["^html$|^htm$|^xhtml$"],
        'HTML_Ruby':   ["^erb$|^rhtml$|^html.erb$"],
        'INI':         ["^ini$|^conf$|^cfg$|^prefs$"],
        'Io':          ["^io$"],
        'Jack':        ["^jack$"],
        'Jade':        ["^jade$"],
        'Java':        ["^java$"],
        'JavaScript':  ["^js$|^jsm$"],
        'JSON':        ["^json$"],
        'JSONiq':      ["^jq$"],
        'JSP':         ["^jsp$"],
        'JSX':         ["^jsx$"],
        'Julia':       ["^jl$"],
        'LaTeX':       ["^tex$|^latex$|^ltx$|^bib$"],
        'Lean':        ["^lean$|^hlean$"],
        'LESS':        ["^less$"],
        'Liquid':      ["^liquid$"],
        'Lisp':        ["^lisp$"],
        'LiveScript':  ["^ls$"],
        'LogiQL':      ["^logic$|^lql$"],
        'LSL':         ["^lsl$"],
        'Lua':         ["^lua$"],
        'LuaPage':     ["^lp$"],
        'Lucene':      ["^lucene$"],
        'Makefile':    ["^Makefile$|^GNUmakefile$|^makefile$|^OCamlMakefile$|^make$"],
        'Markdown':    ["^md$|^markdown$"],
        'Mask':        ["^mask$"],
        'MATLAB':      ["^matlab$"],
        'MEL':         ["^mel$"],
        'MUSHCode':    ["^mc$|^mush$"],
        'MySQL':       ["^mysql$"],
        'Nix':         ["^nix$"],
        'ObjectiveC':  ["^m$|^mm$"],
        'OCaml':       ["^ml$|^mli$"],
        'Pascal':      ["^pas$|^p$"],
        'Perl':        ["^pl$|^pm$"],
        'pgSQL':       ["^pgsql$"],
        'PHP':         ["^php$|^phtml$|^inc|^module|^theme$"],
        'Powershell':  ["^ps1$"],
        'Praat':       ["^praat$|^praatscript$|^psc$|^proc$"],
        'Prolog':      ["^plg$|^prolog$"],
        'Properties':  ["^properties$"],
        'Protobuf':    ["^proto$"],
        'Python':      ["^py$"],
        'R':           ["^r$"],
        'RDoc':        ["^Rd$"],
        'RHTML':       ["^Rhtml$"],
        'Ruby':        ["^rb$|^ru$|^gemspec$|^rake$|^Guardfile$|^Rakefile$|^Gemfile$"],
        'Rust':        ["^rs$"],
        'SASS':        ["^sass$"],
        'SCAD':        ["^scad$"],
        'Scala':       ["^scala$"],
        'Scheme':      ["^scm$|^rkt$"],
        'SCSS':        ["^scss$"],
        'SH':          ["^sh$|^bash$|^.bashrc$"],
        'SJS':         ["^sjs$"],
        'Smarty':      ["^smarty$|^tpl$"],
        'snippets':    ["^snippets$"],
        'Soy_Template':["^soy$"],
        'Space':       ["^space$"],
        'SQL':         ["^sql$"],
        'Stylus':      ["^styl$|^stylus$"],
        'SVG':         ["^svg$"],
        'Tcl':         ["^tcl$"],
        'Tex':         ["^tex$"],
        'Text':        ["^txt$"],
        'Textile':     ["^textile$"],
        'Toml':        ["^toml$"],
        'Twig':        ["^twig$"],
        'Typescript':  ["^ts$|^typescript$|^str$"],
        'Vala':        ["^vala$"],
        'VBScript':    ["^vbs$|^vb$"],
        'Velocity':    ["^vm$"],
        'Verilog':     ["^v$|^vh$|^sv$|^svh$"],
        'VHDL':        ["vhd$|vhdl$"],
        'XML':         ["^xml$|^rdf$|^rss$|^wsdl$|^xslt$|^atom$|^mathml$|^mml$|^xul$|^xbl$|^xaml$"],
        'XQuery':      ["^xq$"],
        'YAML':        ["^yaml$|^yml$"],
    }
    
    SETTINGS_AUTO_CLOSE_BRACKETS = 'editor/editor_helper_auto_close_brackets'
    SETTINGS_USE_TABS_TO_INDENT = 'editor/editor_helper_use_tabs_to_indent'
    
    @classmethod
    def lang_from_file_info(cls, file_info):
        suffix = file_info.suffix()
        for language, info in cls.supportedModes.items():
            regex = re.compile(info[0])
            if regex.match(suffix):
                return language
        return None
    
    @classmethod
    def json_dumps(cls, callback):
        def wrapper(self, *args, **kwargs):
            return json.dumps(callback(self, *args, **kwargs))
        return wrapper
