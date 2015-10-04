#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import hashlib
import pkg_resources

from PyQt5.QtCore import QFileInfo

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from alter import ModuleManager
from .model import File, Class, Function

Settings = ModuleManager.core['settings'].Settings
EditorHelper = ModuleManager.core['ace_editor'].EditorHelper
Navigation = ModuleManager.core['navigation'].Navigation



class FileInspectorHelper:
    """docstring for FileInspectorHelper"""
    
    regex = {
        'Python': {
            'class' : re.compile(r"^class (?P<name>[a-zA-Z0-9_]*)\(?(?P<inherits>[a-zA-Z0-9_]*)\)?:\n(?P<content>(?P<last_line> {4,}.*\r?\n?)*)", re.M),
            'method': re.compile(r"^\n? {4,}def (?P<name>[a-zA-Z0-9_]*)\((?P<args>.*)\):", re.M),
            'function': re.compile(r"^def (?P<name>[a-zA-Z0-9_]*)\((?P<args>.*)\):", re.M),
        }
    }
    
    session = None
    
    @classmethod
    def session_maker(cls):
        if not cls.session:
            filename = 'file_inspector.db'
            pkg = 'file_inspector'
            db_path = pkg_resources.resource_filename(pkg, filename)
            engine = create_engine('sqlite:////'+db_path)
            Session = sessionmaker(bind=engine)
            cls.session = Session()
    
    @classmethod
    def query(cls, *args, **kwargs):
        cls.session_maker()
        return cls.session.query(*args, **kwargs)
    
    @classmethod
    def insert_file(cls, file_info, commit=False):
        path = file_info.absoluteFilePath()
        lang = EditorHelper.lang_from_file_info(file_info)
        new_file = None
        if lang in cls.regex:
            with open(path, 'r') as f:
                content = f.read()
                name = file_info.fileName()
                project = Settings.value(Navigation.SETTINGS_CURRENT_DIR, '')
                checksum = hashlib.md5(content.encode()).hexdigest()
                new_file = File(
                    path=path, project=project, name=name, checksum=checksum)
                new_file.classes = cls.get_classes(new_file, content, lang)
                new_file.functions = cls.get_functions(new_file, content, lang)
                cls.session_maker()
                cls.session.add(new_file)
                if commit:
                    cls.session.commit()
        return new_file
    
    @classmethod
    def get_classes(cls, file, content, lang):
        classes = []
        for match in cls.regex[lang]['class'].finditer(content):
            name = match.group('name')
            inherits = match.group('inherits')
            content = match.group('content')
            classe = Class(name=name, inherits=inherits, file=file)
            classe.methods = cls.get_methods(file, content, lang)
            classes.append(classe)
        return classes
    
    @classmethod
    def get_methods(cls, file, content, lang):
        methods = []
        for match in cls.regex[lang]['method'].finditer(content):
            name = match.group('name')
            args = match.group('args')
            method = Function(name=name, args=args, file=file.id)
            methods.append(method)
        return methods
    
    @classmethod
    def get_functions(cls, file, content, lang):
        functions = []
        for match in cls.regex[lang]['function'].finditer(content):
            name = match.group('name')
            args = match.group('args')
            function = Function(name=name, args=args, file=file.id)
            functions.append(function)
        return functions