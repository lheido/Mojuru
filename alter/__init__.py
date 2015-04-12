#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
    This module provide a static class for alterate some code.
    Inspired by the Drupal hook system.
    Another static class ModuleManager provide functions to load/reload 
    modules.
    
    Module structure:
        module_name/
            __init__.py -> see ModuleInfo.__doc__
            module_name.py
            other_file.py
            another_file.py
"""

__version__ = "0.2.9"

from .Alter import Alter
from .ModuleManager import ModuleManager
from .ModuleManager import ModuleInfo