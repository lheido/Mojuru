#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QFileInfo
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QAction

from alter import Alter

@Alter.alter('main_window_add_horizontal_widget')
def add_horizontal_widget(horizontal_widgets, parent):
    horizontal_widgets.append(TabWidget(parent))


class TabWidget(QTabWidget):
    """
    TabWidget class definition
    """
    
    def __init__(self, parent=None):
        super(TabWidget, self).__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        
        self.tabCloseRequested.connect(self.on_tab_closed)
        
        self.menu_button = QPushButton('Menu', self)
        self.menu_button.clicked.connect(self.on_menu_button_clicked)
        self.menu_button.setObjectName('TabWidgetMenuButton')
        self.menu_button.setToolTip('Menu with useful actions')
        self.setCornerWidget(self.menu_button, Qt.TopRightCorner)
        self.menu = QMenu(self)
        self.add_action('Remove current tab', 'ctrl+w', TabWidgetHelper.remove)
        self.add_action(
            'Remove all tab', 'ctrl+shift+w', TabWidgetHelper.remove_all)
        self.add_separator()
        self.add_action('Next Tab', QKeySequence.NextChild, 
                        TabWidgetHelper.next_tab)
        self.add_action('Previous Tab', QKeySequence.PreviousChild, 
                        TabWidgetHelper.previous_tab)
        # @ToDO Alter.invoke_all('tab_widget_add_action', self)
    
    # the function name must be equal to signal name.
    # decorator because reduce the amount of memory used and is slightly faster
    @pyqtSlot(QFileInfo)
    def onFileItemActivated(self, file_info):
        pass
    
    def on_menu_button_clicked(self):
        pos = self.mapToGlobal(self.menu_button.pos())
        menu_width = self.menu.sizeHint().width()
        pos.setY(pos.y() + self.menu_button.height())
        pos.setX(pos.x() + self.menu_button.width() - menu_width)
        if len(self.menu.actions()) > 0:
            self.menu.exec(pos)
    
    def on_tab_closed(self, index):
        widget = self.widget(index)
        self.removeTab(index)
        # remove the widget for real
        widget.deleteLater()
        del widget
    
    def add_action(self, name, shortcut, callback, icon = None):
        """
        Ajoute une action au context menu et au widget navigation lui même.
        Créer une fonction à la volé pour fournir des arguments aux fonctions
        associé aux actions.
        """
        action = QAction(name, self)
        if icon:
            action.setIcon(icon)
        action.setShortcut(shortcut)
        action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        action.triggered.connect(self.__wrapper(callback))
        self.addAction(action)
        self.menu.addAction(action)

    def add_separator(self):
        """Simple abstraction of self.context_menu.addSeparator()"""
        self.menu.addSeparator()
    
    def __wrapper(self, callback):
        def __new_function():
            """
            __new_function représente la forme de tous les callbacks connecté
            à une action pour pouvoir utiliser les raccourcis en même temps que
            le menu contextuel.
            """
            callback(self)
        return __new_function


class TabWidgetHelper:
    """
    Basic helper define actions.
    """
    
    @classmethod
    def remove(cls, tab_widget):
        tab_widget.tabCloseRequested.emit(tab_widget.currentIndex())
    
    @classmethod
    def remove_all(cls, tab_widget):
        for i in reversed(range(tab_widget.count())):
            tab_widget.tabCloseRequested.emit(i)
    
    @classmethod
    def next_tab(cls, tab_widget):
        index = tab_widget.currentIndex() + 1
        if tab_widget.currentIndex() == tab_widget.count() - 1:
            index = 0
        tab_widget.setCurrentIndex(index)
    
    @classmethod
    def previous_tab(cls, tab_widget):
        index = tab_widget.currentIndex() - 1
        if tab_widget.currentIndex() == 0:
            index = tab_widget.count() - 1
        tab_widget.setCurrentIndex(index)