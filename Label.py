#! /usr/bin/python
#encoding=utf-8
#author: fakir

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class Label(QLabel):
    clicked = pyqtSignal()
    def __init__(self, text, parent=None):
        QLabel.__init__(self, text, parent)

    def __init__(self, parent=None):
        QLabel.__init__(self, parent)

    def mousePressEvent(self, event):
        self.clicked.emit()
        QLabel.mousePressEvent(self, event)


