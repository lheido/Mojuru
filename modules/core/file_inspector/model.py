#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pkg_resources

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
filename = 'file_inspector.db'
pkg = 'file_inspector'
db_path = pkg_resources.resource_filename(pkg, filename)
engine = create_engine('sqlite:////'+db_path)


class File(Base):
    __tablename__ = 'file'
    __table_args__ = {'sqlite_autoincrement': True}
    
    id = Column(Integer, primary_key=True)
    path = Column(String, nullable=False)
    name = Column(String, nullable=False)
    project = Column(String)
    checksum = Column(String)
    classes = relationship('Class', cascade="all, delete, delete-orphan")
    functions = relationship('Function', cascade="all, delete, delete-orphan")
    
    def __repr__(self):
        _repr = "<File(id={0}, name='{1}', classes={2}, functions={3})>"
        return _repr.format(self.id, self.name, self.classes, self.functions)


class Class(Base):
    __tablename__ = 'class'
    __table_args__ = {'sqlite_autoincrement': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    inherits = Column(String, nullable=True)
    parent = Column(ForeignKey('class.id'), nullable=True)
    methods = relationship('Function', cascade="all, delete, delete-orphan")
    file = Column(ForeignKey('file.id'))
    
    def __repr__(self):
        _repr = "\n\t<Class(id={0}, name='{1}', methods=\n\t\t{2})>"
        return _repr.format(self.id, self.name, self.methods)


class Function(Base):
    __tablename__ = 'function'
    __table_args__ = {'sqlite_autoincrement': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    args = Column(String, nullable=True)
    classe = Column(ForeignKey('class.id'), nullable=True)
    parent = Column(ForeignKey('function.id'), nullable=True)
    file = Column(ForeignKey('file.id'))
    
    def __repr__(self):
        _repr = "<Function(id={0}, name='{1}', classe={2}, parent={3}, file={4})>"
        return _repr.format(self.id, self.name, self.classe, self.parent, self.file)


# Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
