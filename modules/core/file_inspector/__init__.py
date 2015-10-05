#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
File inspector widget core module.
Provide a widget to display infos about the current file for the programing 
languages.
Provide a SQLite bdd to store class, methods and more.
"""

name = "File Inspector"

dependencies = [
    'settings',
    'navigation',
    'tab_widget',
    'ace_editor'
]

# alterations = [
#     'tab_widget_add_tab',
#     'tab_widget_add_action'
# ]

switched_off = False

weight = 3