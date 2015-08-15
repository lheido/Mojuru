#!/usr/bin/python3
# -*- coding: utf-8 -*-

from alter import Alter
from alter import ModuleManager


@Alter.alter('editor_widget_init')
def default_config_languages_init(ace_editor):
    language = ace_editor.language
    
    if language in ['PHP','HTML','CSS','SCSS','JavaScript','LESS','Twig']:
        ace_editor.status_bar.set_tab_size(2)
        ace_editor.editor_actions['Use soft tabs'].setChecked(True)
        
    elif language == 'Python':
        ace_editor.editor_actions['Use soft tabs'].setChecked(True)
        