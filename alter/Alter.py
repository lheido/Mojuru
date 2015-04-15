#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
    Implementation of static class Alter.
    Inspired by the Drupal hook system.
    Allow to define some functions to alter an other 
    (sort of module/plugin/bundle).
    
    How to use:
        from alter import Alter
        
        # In module use this decorator
        @Alter.alter('alter')
        def foo(): # args provide by alterations who define alter 'alter'
            pass
        
        # In module or script who define alter 'alter' :
        >> invoke('alter', 'module_name', arg1, arg2, ...)
        >> invoke_all('alter', arg1, arg2, ...)
        
        Assume that your alterations is registered before loading modules with :
        >> Alter.register('alter')
"""
import collections

from .exceptions import NotRegisteredModule
from .exceptions import NotRegisteredAlteration
from .exceptions import StaticClassException


class Alter:
    """
    Static class provide alter decorator, register, invoke and invoke all 
    static methods.
    Don't instanciate this class.
    """
    
    alterations = collections.OrderedDict()
    
    def __init__(self):
        raise StaticClassException(self.__class__.__name__)
    
    @classmethod
    def register(cls, alter):
        """
        Register an alteration name.
        """
        if alter not in cls.alterations.keys():
            cls.alterations[alter] = collections.OrderedDict()
    
    @classmethod
    def alter(cls, alter):
        """
        Decorator to link function with an alteration.
        """
        if alter in cls.alterations.keys():
            def decorator(obj):
                # __module__ == 'module_name.module_name' in agreement with 
                # the module structure.
                # So we just split by '.'.
                module_name = obj.__module__.split('.')[0]
                if module_name not in cls.alterations[alter].keys():
                    cls.alterations[alter][module_name] = []
                cls.alterations[alter][module_name].append(obj)
            return decorator
        else:
            def foo(obj):
                return obj
            return foo
    
    @classmethod
    def invoke_all(cls, alter, *args):
        """
        Invoke all function decorated by alter(alter)
        """
        if alter in cls.alterations.keys():
            for module_name in cls.alterations[alter]:
                cls.invoke(alter, module_name, *args)
        else:
            raise NotRegisteredAlteration(alter)
    
    @classmethod
    def invoke(cls, alter, module_name, *args):
        """
        Invoke the function decorated by alter(alter) in module.
        """
        if alter in cls.alterations.keys():
            if module_name in cls.alterations[alter].keys():
                for fun in cls.alterations[alter][module_name]:
                    fun(*args)
            else:
                raise NotRegisteredModule(module_name, alter)
        else:
            raise NotRegisteredAlteration(alter)
