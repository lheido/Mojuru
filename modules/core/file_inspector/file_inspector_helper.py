#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import hashlib
import pkg_resources

from PyQt5.QtCore import QFileInfo

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
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
            'method': re.compile(r"^\n? {4}def (?P<name>[a-zA-Z0-9_]*)\((?P<args>.*)\):", re.M),
            'function': re.compile(r"^def (?P<name>[a-zA-Z0-9_]*)\((?P<args>.*)\):", re.M),
        },
        'PHP': {
            'class': re.compile(r"^class (?P<name>[a-zA-Z0-9_]*) ?\r?\n?\{(?P<content>(?P<last_line>\r?\n? {2,}.*\r?\n?)*)\}", re.M),
            'method': re.compile(r"(?P<access>public|protected|private)? (?P<static>static)?(?P=static)? ?function (?P<name>[a-zA-Z0-9_]*) ?\((?P<args>.*)\)", re.M),
            'function': re.compile(r"^function (?P<name>[a-zA-Z0-9_]*) ?\((?P<args>.*)\)", re.M)
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
    def _one(cls, query):
        try:
            return query.one()
        except NoResultFound as e:
            return None
        except MultipleResultsFound as e:
            raise e
    
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
                if not path.startswith(project):
                    project = None
                checksum = hashlib.md5(content.encode()).hexdigest()
                new_file = File(
                    path=path, project=project, name=name, checksum=checksum)
                cls.get_classes(new_file, content, lang)
                cls.get_functions(new_file, content, lang)
                cls.session_maker()
                cls.session.add(new_file)
                if commit:
                    cls.session.commit()
        return new_file
    
    @classmethod
    def update_file(cls, file_info, commit=False):
        path = file_info.absoluteFilePath()
        lang = EditorHelper.lang_from_file_info(file_info)
        file = cls.get_or_insert_file(file_info)
        if lang in cls.regex and file:
            with open(path, 'r') as f:
                content = f.read()
                checksum = hashlib.md5(content.encode()).hexdigest()
                if file.checksum != checksum:
                    file.checksum = checksum
                    cls.get_classes(file, content, lang)
                    cls.get_functions(file, content, lang)
                    if commit:
                        cls.session.commit()
        return file
    
    @classmethod
    def get_or_insert_file(cls, file_info):
        file_path = file_info.absoluteFilePath()
        db_file = cls._one(FileInspectorHelper.query(File).\
            filter(File.path == file_path))
        if db_file is None:
            db_file = FileInspectorHelper.insert_file(file_info, True)
        return db_file
    
    @classmethod
    def get_classes(cls, file, content, lang):
        classes = []
        for match in cls.regex[lang]['class'].finditer(content):
            name = match.group('name')
            inherits = match.group('inherits')
            content = match.group('content')
            classe = cls._get_classe(file, name)
            if not classe:
                classe = Class(name=name, inherits=inherits, file=file.id)
                file.classes.append(classe)
            cls.get_methods(file, classe, content, lang)
            classes.append(classe)
        #clean classes
        for i, classe in enumerate(file.classes):
            if classe not in classes:
                del file.classes[i]
    
    @classmethod
    def _get_classe(cls, file, name):
        for classe in file.classes:
            if classe.name == name:
                return classe
        return None
    
    @classmethod
    def get_methods(cls, file, classe, content, lang):
        methods = []
        for match in cls.regex[lang]['method'].finditer(content):
            name = match.group('name')
            args = match.group('args')
            method = cls._get_method(classe, name)
            if not method:
                method = Function(name=name, args=args, classe=classe.id)
                classe.methods.append(method)
            methods.append(method)
        #clean methods
        for i, method in enumerate(classe.methods):
            if method not in methods:
                del classe.methods[i]
    
    @classmethod
    def _get_method(cls, classe, name):
        for method in classe.methods:
            if method.name == name:
                return method
        return None
    
    @classmethod
    def get_functions(cls, file, content, lang):
        functions = []
        for match in cls.regex[lang]['function'].finditer(content):
            name = match.group('name')
            args = match.group('args')
            function = cls._get_function(file, name)
            if not function:
                function = Function(name=name, args=args, file=file.id)
                file.functions.append(function)
            functions.append(function)
        #clean functions
        for i, function in enumerate(file.functions):
            if function not in functions:
                del file.functions[i]
    
    @classmethod
    def _get_function(cls, file, name):
        for function in file.functions:
            if function.name == name:
                return function
        return None