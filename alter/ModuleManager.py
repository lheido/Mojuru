#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Implementation of static class ModuleManager and ModuleInfo class.    
"""
import os
import sys
import importlib
import collections

from .Alter import Alter
from .exceptions import StaticClassException


class ModuleManager:
    
    def __init__(self):
        raise StaticClassException(self.__class__.__name__)
    
    @classmethod
    def add_module_directory(cls, dir_attr_name, dir_path):
        setattr(cls, dir_attr_name, collections.OrderedDict())
        setattr(cls, "path_{0}".format(dir_attr_name), dir_path)
    
    @classmethod
    def load_info(cls, module_name):
        return ModuleInfo(module_name)
    
    @classmethod
    def load(cls, module_name, module_directory):
        getattr(cls, module_directory)[module_name] = importlib.import_module(
            "{0}.{0}".format(module_name))
    
    @classmethod
    def load_all(cls, module_directory):
        # append modules directory path to sys.path
        path = getattr(cls, "path_{0}".format(module_directory))
        if path not in sys.path:
            sys.path.append(path)
        
        modules_list = [cls.load_info(module) for module in os.listdir(path)]
        modules_list = cls.dependency_sort(modules_list)
        
        for moduleInfo in modules_list:
            # alteration registrations
            for alteration in moduleInfo.alterations:
                Alter.register(alteration)
            
            # load module
            cls.load(moduleInfo.module_name, module_directory)
    
    @classmethod
    def reload_module(cls, module_name, module_directory):
        moduleInfo = cls.load_info(module_name)
        if moduleInfo.reloadable:
            getattr(cls, module_directory)[module_name] = importlib.reload(
                getattr(cls, module_directory)[module_name])
    
    @classmethod
    def reload_all_modules(cls, module_directory):
        for module_name in getattr(cls, module_directory).keys():
            cls.reload_module(module_name, module_directory)
    
    @classmethod
    def _set_attr_name(cls, module_name):
        setattr(cls, module_name, cls.modules[module_name])
    
    @classmethod
    def dependency_sort(cls, modules):
        i, new_list, copy = 0, [], [module for module in modules]
        while copy != []:
            find = len(copy[i].dependencies)
            for name in copy[i].dependencies:
                for loaded in new_list:
                    if name == loaded.module_name:
                        find -= 1
            if find == 0:
                new_list.append(copy.pop(i))
                i = 0
            else:
                i += 1
        return new_list


class ModuleInfo:
    """
    A module come with (all params are optional):
        - name: human readable name.
        - module_name:  package_name by default.
        - description: the module description.
        - dependencies: the module_name list. (not yet)
        - alterations: alterations to register.
        - switched_off: the module can be disable (set to True) or not.
        - reloadable: the module can be reloaded
        - weight: the module weight to ordering invocation.
    """
    name = ''
    module_name = ''
    description = ''
    dependencies = []
    alterations = []
    switched_off = True
    reloadable = True
    weight = 0
    
    def __init__(self, module_name):
        module = importlib.import_module(module_name)
        module = importlib.reload(module)
        self.name = self.module_name = module.__name__
        self.description = module.__doc__.strip() if module.__doc__ else ''
        for key, value in module.__dict__.items():
            if key in dir(self):
                setattr(self, key, value)
        
    def __dir__(self):
        return ['name', 'module_name', 'description', 'dependencies', 
                'alterations', 'switched_off', 'reloadable', 'weight']