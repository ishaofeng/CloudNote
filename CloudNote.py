#! /usr/bin/python
#encoding=utf-8
#author: fakir

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import datetime

from config import *

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from YouDaoCloudService import YouDaoCloudService
from DBManager import Notebook, Note
from KindEditor import KindEditor
from Label import Label
from SearchWidget import SearchWidget

class CloudNote(QDialog):
    NOTE_FORMAT = "<img src=\"resources/image/note16.png\"/>%s<br/><font color=\"green\" size=\"12px\">%s</font>%s"

    def __init__(self, cloudService, db, conf, logger):
        QDialog.__init__(self)

        self.setWindowTitle("CloudNote")

        self.cloudService = cloudService
        self.db = db
        self.conf = conf
        self.logger = logger
        self.cache = {}

        self.__initMainGui()
        self.__initNotebookTree()
        self.__setNoteList()

    def __initMainGui(self):
        mainLayout = QVBoxLayout(self)
        mainLayout.setSpacing(0)
        mainLayout.setMargin(0)

        #顶部
        self.titleBar= QToolBar(self)
        self.titleBar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.titleBar.addAction(QIcon("resources/image/notebook.png"), u"添加笔记本", self, SLOT("__addNotebook()"))
        self.titleBar.addSeparator()
        self.titleBar.addAction(QIcon("resources/image/note.png"), u"添加笔记", self, SLOT("__addNote()"))

        #左侧树形结构
        self.leftTreeWidget = QWidget(self)
        self.leftTreeWidget.setMinimumWidth(200)
        self.leftTreeWidget.setMaximumWidth(300)
        leftTreeLayout = QVBoxLayout(self)
        leftTreeLayout.setSpacing(0)
        leftTreeLayout.setMargin(0)

        ##树形结构
        self.treeWidget = QTreeWidget(self)
        self.treeWidget.setHeaderHidden(True)
        self.treeWidget.setColumnCount(1)
        self.allNoteTreeItem = QTreeWidgetItem()
        self.allNoteTreeItem.setText(0, u"全部笔记")
        self.treeWidget.addTopLevelItem(self.allNoteTreeItem)
        leftTreeLayout.addWidget(self.treeWidget)
        self.leftTreeWidget.setLayout(leftTreeLayout)
        self.treeWidget.setContextMenuPolicy(Qt.CustomContextMenu)

        self.treeWidget.itemDoubleClicked.connect(self.__treeItemDoubleClicked)
        self.treeWidget.itemClicked.connect(self.__treeItemClicked)

        self.treeWidget.customContextMenuRequested.connect(self.__treeMenu)


        #中间列表结构
        self.middleListWidget = QWidget(self)
        self.middleListWidget.setMinimumWidth(200)
        self.middleListWidget.setMaximumWidth(300)
        middleListLayout = QVBoxLayout(self)
        middleListLayout.setSpacing(0)
        middleListLayout.setMargin(0)

        ##搜索框
        self.searchWidget = SearchWidget(self)
        self.searchWidget.search.connect(self.__search)
        middleListLayout.addWidget(self.searchWidget)

        ##列表结构
        self.noteListWidget = QListWidget(self)
        middleListLayout.addWidget(self.noteListWidget)
        self.noteListWidget.itemClicked.connect(self.__listItemClicked)

        self.middleListWidget.setLayout(middleListLayout)

        #右侧编辑结构
        self.rightEditWidget = QWidget(self)
        rightEditLayout = QVBoxLayout(self)
        rightEditLayout.setSpacing(0)
        rightEditLayout.setMargin(0)

        self.kindEditor = KindEditor()
        self.kindEditor.loadEditor()

        rightEditLayout.addWidget(self.kindEditor)

        self.rightEditWidget.setLayout(rightEditLayout)


        self.splitter = QSplitter(self)
        self.splitter.setHandleWidth(1)
        self.splitter.addWidget(self.leftTreeWidget)
        self.splitter.addWidget(self.middleListWidget)
        self.splitter.addWidget(self.rightEditWidget)
        self.splitter.setStretchFactor(0, 2)
        self.splitter.setStretchFactor(1, 3)
        self.splitter.setStretchFactor(2, 8)

        mainLayout.addWidget(self.titleBar)
        mainLayout.addWidget(self.splitter)

        self.setLayout(mainLayout)

    def __initNotebookTree(self):
        session = self.db.createSession()

        notebooks = session.query(Notebook.path, Notebook.name).all()
        for notebookpath, name in notebooks:
            notesize = len(session.query(Note.path,Note.title, Note.create_time, Note.summary).filter(Note.path.like(notebookpath + "%")).all())

            notebookitem = self.__createTreeItem(notebookpath, "%s  (%d)" % (name, notesize), False)

            self.allNoteTreeItem.addChild(notebookitem)


        self.allNoteTreeItem.setExpanded(True)
        self.allNoteTreeItem.setSelected(True)

    def __setTreeItemText(self, item, text):
        item.setText(u"%s  (%d)" % (text, item.childCount()))

    def __getTreeItemText(self, item):
        text = item.text().split("  (")[0]
        return text

    def __setNoteList(self):
        self.noteListWidget.clear()

        session = self.db.createSession()
        pathfilter = ""

        items = self.treeWidget.selectedItems()
        if len(items) > 0:
            pathfilter = str(items[0].whatsThis(0))

        notes = []
        if pathfilter == "":
            notes = session.query(Note.path,Note.title,Note.create_time, Note.summary).all()
        else:
            notes = session.query(Note.path,Note.title, Note.create_time, Note.summary).filter(Note.path.like(pathfilter + "%")).all()

        for notepath, title, time, summary in notes:
            time = datetime.date.fromtimestamp(time).strftime("%Y-%m-%d")
            self.__createListItem(self.noteListWidget, notepath, title, time, summary)


    def __createTreeItem(self, path, name, bNote):
        item = QTreeWidgetItem()
        item.setText(0, name)
        item.setWhatsThis(0, path)
        if bNote == True:
            item.setIcon(0, QIcon("resources/image/note.png"))
        else:
            item.setIcon(0, QIcon("resources/image/notebook.png"))

        return item

    def __createListItem(self, widget, path, name, time, summary):
        item = QListWidgetItem()
        item.setSizeHint(QSize(100, 50))
        label = Label(widget)
        label.clicked.connect(self.__listItemClicked)
        label.setFocusProxy(widget)
        label.setFixedHeight(50)
        label.setText(CloudNote.NOTE_FORMAT % (name, time, summary))

        label.setWhatsThis(path)

        widget.addItem(item)
        widget.setItemWidget(item, label)

        return item

    def __treeItemDoubleClicked(self, item, column):
        self.__setNoteList()

    def __treeItemClicked(self, item, column):
        self.__setNoteList()

    def __listItemClicked(self):
        item = self.sender()

        session = self.db.createSession()
        path = str(item.whatsThis())

        note = session.query(Note).filter_by(path=path).first()

        self.kindEditor.setNote(note)

    def __treeMenu(self, pos):
       print "hello"

    def __search(self, text):
        print "search"

    def __addNotebook(self):
        pass

    def __addNote(self):
        pass



if __name__ == "__main__":
    app = QApplication([])
    conf = getConf()
    service = YouDaoCloudService(conf)

    w = CloudNote(service)
    w.show()

    app.exec_()
