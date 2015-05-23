#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Tab widget core module.
provide widget with 2 splitter (horizontal|vertical) of QTabWidget

"""

name = "Tab Widget"

dependencies = [
    'settings',
    'navigation'
]

alterations = [
    'tab_widget_add_tab',
    'tab_widget_add_action'
]

switched_off = False

weight = 3