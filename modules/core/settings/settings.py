#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@TODO
"""

from PyQt5.QtCore import QSettings

from alter.exceptions import StaticClassException


class Settings:
    """
    Static class to manage settings.
    """
    
    settings = QSettings('lheido', 'Mojuru')
    
    def __init__(self):
        raise StaticClassException(self.__class__.__name__)
    
    @classmethod
    def sync(cls):
        cls.settings.sync()
    
    @classmethod
    def set_value(cls, name, value, auto_sync=True):
        if not isinstance(value, list):
            cls.settings.setValue(name, value)
        else:
            cls.settings.beginWriteArray(name)
            for i, elt in enumerate(value):
                cls.settings.setArrayIndex(i)
                cls.settings.setValue('{0}-item{1}'.format(name, i), elt)
            cls.settings.endArray()
        if auto_sync:
            cls.sync()
    
    @classmethod
    def value(cls, name, default_value, is_array=False):
        if not is_array:
            return cls.settings.value(name, default_value)
        else:
            result = []
            array_size = cls.settings.beginReadArray(name)
            for i in range(array_size):
                cls.settings.setArrayIndex(i)
                result.append(cls.settings.value('{0}-item{1}'.format(name, i)))
            cls.settings.endArray()
            return result