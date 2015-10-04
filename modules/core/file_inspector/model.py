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
    path = Column(String)
    name = Column(String)
    project = Column(String)
    checksum = Column(String)
    classes = relationship('Class')
    functions = relationship('Function')
    
    def __repr__(self):
        _repr = "<File(\n\tname='{0}',\n\tpath='{1}',\n\tproject='{2}',\n\tchecksum='{3}',\n\tclasses={4}\n)>"
        return _repr.format(self.name, self.path, self.project, self.checksum, self.classes)


class Class(Base):
    __tablename__ = 'class'
    __table_args__ = {'sqlite_autoincrement': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    inherits = Column(String, nullable=True)
    parent = Column(ForeignKey('class.id'), nullable=True)
    methods = relationship('Function')
    file = Column(ForeignKey('file.id'))
    
    def __repr__(self):
        _repr = "\n<Class(\n\tname='{0}',\n\tinherits='{1}',\n\tparent='{2}',\n\tfile={3},\n\tmethods={4}\n)>"
        return _repr.format(self.name, self.inherits, self.parent, self.file, self.methods)


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
        _repr = "\n<Function(\n\tname='{0}',\n\targs='{1}',\n\tclasse='{2}',\n\tparent='{3}'\n)>"
        return _repr.format(self.name, self.args, self.classe, self.parent)

Base.metadata.create_all(engine)
# Base.metadata.drop_all(engine)