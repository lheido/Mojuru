#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Editor widget based on QWebView and ace javascript web editor.

"""

name = "Ace Editor Widget"

dependencies = [
    'settings',
    'tab_widget'
]

alterations = [
    'editor_presave',
    'editor_save'
]

switched_off = False

weight = 4