#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Mojuru Main
"""
import sys
import os.path

from PyQt5.QtCore import QFileInfo
from PyQt5.QtWidgets import QApplication

from alter import Alter, ModuleManager

Alter.register('mojuru_init')
Alter.register('mojuru_set_main_window')

class Mojuru(QApplication):
    
    app_path = QFileInfo(__file__).absoluteDir().absolutePath()
    
    core_path = os.path.join(app_path, 'modules', 'core')
    custom_path = os.path.join(app_path, 'modules', 'custom')
    
    def __init__(self, argv):
        super(Mojuru, self).__init__(argv)
        
        ModuleManager.add_module_directory('core', self.core_path)
        ModuleManager.add_module_directory('custom', self.custom_path)
        
        ModuleManager.load_all('core')
        ModuleManager.load_all('custom')
        
        Alter.invoke_all('mojuru_init', self)
    
    def run(self):
        Alter.invoke_all('mojuru_set_main_window', self)
        self.exec_()

if __name__ == "__main__":
    Mojuru(sys.argv).run()
