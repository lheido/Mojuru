#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
    Define exceptions raised by the lib.
"""

class NotRegisteredAlteration(Exception):

    def __init__(self, alter):
        message = "The " + alter + " alteration is not registered."
        super(NotRegisteredAlteration, self).__init__(message)


class NotRegisteredModule(Exception):

    def __init__(self, module, alter):
        message = "The {0} module is not registered in {1} alteration."
        message = message.format(module, alter)
        super(NotRegisteredModule, self).__init__(message)


class StaticClassException(Exception):
    
    def __init__(self, class_name):
        message = "{0} class is a static class, you should not instantiate it."
        message = message.format(class_name)
        super(StaticClassException, self).__init__(message)