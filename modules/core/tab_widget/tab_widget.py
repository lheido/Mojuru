#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QFileInfo
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QEvent
from PyQt5.QtGui import QKeySequence
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QAction

from alter import Alter

@Alter.alter('main_window_add_horizontal_widget')
def add_horizontal_widget(horizontal_widgets, parent):
    horizontal_widgets["tab_widget"] = TabWidget(parent)
    policy = horizontal_widgets["tab_widget"].sizePolicy()
    # use "maximum" space available horizontally
    policy.setHorizontalStretch(14)
    horizontal_widgets["tab_widget"].setSizePolicy(policy)

@Alter.alter('main_window_connect_widgets')
def connect_widgets(vertical_widgets, horizontal_widgets):
    getattr(horizontal_widgets['navigation'], 'onFileItemActivated').connect(
        getattr(horizontal_widgets['tab_widget'], 'onFileItemActivated'))


class TabWidget(QTabWidget):
    """
    TabWidget class definition
    """
    
    def __init__(self, parent=None):
        super(TabWidget, self).__init__(parent)
        self.tabBar().installEventFilter(self)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setFocusPolicy(Qt.NoFocus)
        
        self.icon_modified = QIcon('images/is-modified.png')
        self.icon_not_modified = QIcon('images/is-not-modified.png')
        
        self.tabCloseRequested.connect(self.on_tab_closed)
        
        nav_icon = QIcon('images/navigation-menu.png')
        self.menu_button = QPushButton('', self)
        self.menu_button.setIcon(nav_icon)
        self.menu_button.setFlat(True)
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
        Alter.invoke_all('tab_widget_add_action', self)
        self.currentChanged[int].connect(self.on_current_changed)
    
    def eventFilter(self, o, event):
        if o == self.tabBar() and event.type() == QEvent.MouseButtonPress:
            index = self.tabBar().tabAt(event.pos())
            if index != -1:
                self.on_tab_closed(index)
                return True
        return super(TabWidget, self).eventFilter(o, event)
    
    def on_current_changed(self, index):
        if index != -1:
            self.setFocusProxy(self.widget(index))
            self.setFocus(Qt.TabFocusReason)
    
    # the function name must be equal to signal name.
    # decorator because reduce the amount of memory used and is slightly faster
    @pyqtSlot(QFileInfo)
    def onFileItemActivated(self, file_info):
        Alter.invoke_all('tab_widget_add_tab', self, file_info)
    
    def add_tab(self, cls, file_info, force_open=False):
        #if file is already open
        index, i = -1, 0
        while not force_open and i < self.count() and index == -1:
            if self.widget(i).file_info == file_info:
                index = i
            i += 1
        if index == -1:
            index = self.addTab(
                cls(file_info, self),
                self.icon_not_modified,
                file_info.fileName()
            )
        self.setCurrentIndex(index)
        self.setFocus(True)
    
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
    
    def on_current_modified(self, modified):
        icon = self.icon_modified if modified else self.icon_not_modified
        index = self.currentIndex()
        self.tabBar().setTabIcon(index, icon)


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