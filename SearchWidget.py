#! /usr/bin/python
#encoding=utf-8
#author: fakir


from PyQt4.QtGui import *
from PyQt4.QtCore import *


class SearchWidget(QWidget):
    search = pyqtSignal(str)
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        with open("resources/qss/SearchWidget.qss") as f:
            self.setStyleSheet(f.read())


        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)

        self.searchLabel = QLabel(self)
        self.searchLabel.setFixedHeight(32)
        self.searchLabel.setFixedWidth(32)
        self.searchLabel.setObjectName("searchLabel")
        self.searchLineEdit = QLineEdit(self)
        self.searchLineEdit.setFixedHeight(32)
        self.searchLineEdit.setObjectName("searchLineedit")
        self.searchLineEdit.returnPressed.connect(self.__returnPressed)
        #self.searchButton = QPushButton(u"搜索", self)
        #self.searchButton.setFixedHeight(32)
        #self.searchButton.setObjectName("searchButton")

        layout.addWidget(self.searchLabel)
        layout.addWidget(self.searchLineEdit)
        #layout.addWidget(self.searchButton)

        self.setLayout(layout)

    def __returnPressed(self):
        self.search.emit(self.searchLineEdit.text())


