#! /usr/bin/python
#coding=utf-8

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import os

from LocalServer import runServer
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *
from PyQt4.QtNetwork import *
from datetime import datetime


class KindEditor(QWidget):
    jsInvokeQt = pyqtSignal()

    DEFAULT_SERVER = "http://127.0.0.1:9876"
    CREATE_TIME_FORMAT = u"创建时间: %s"
    MODIFY_TIME_FORMAT = u"修改时间: %s"
    SOURCE_FORMAT = u"来源: <a href=\"%s\">%s</a>"
    def __init__(self, conf=None, logger=None, parent=None):
        QWidget.__init__(self, parent)
        self.conf = conf
        self.logger = logger

        self.__setStyleSheet()

        self.btn = QPushButton(self)
        self.btn.setVisible(False)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setMargin(0)

        #笔记元信息
        titleLayout = QHBoxLayout()
        titleLayout.setSpacing(0)
        titleLayout.setMargin(0)

        self.titleLineEdit = QLineEdit(self)
        self.titleLineEdit.setFixedHeight(24)
        self.titleLineEdit.setPlaceholderText(u"点击输入标题")
        titleLayout.addWidget(self.titleLineEdit)
        self.detailButton = QPushButton(u"显示详细", self)
        self.detailButton.setFlat(True)
        titleLayout.addWidget(self.detailButton)
        self.detailButton.setFixedHeight(24)
        self.detailButton.clicked.connect(self.__detailButtonClicked)
        self.layout.addLayout(titleLayout)

        self.metaWidget = QWidget(self)
        self.metaWidget.setObjectName("metaWidget")
        self.metaWidget.setFixedHeight(24)
        metaLayout = QHBoxLayout()
        metaLayout.setSpacing(0)
        metaLayout.setMargin(0)

        self.createTimeLabel = QLabel(KindEditor.CREATE_TIME_FORMAT % "", self)
        self.createTimeLabel.setFixedWidth(170)
        self.createTimeLabel.setObjectName("createTimeLabel")
        metaLayout.addWidget(self.createTimeLabel)
        self.modifyTimeLabel = QLabel(KindEditor.MODIFY_TIME_FORMAT % "", self)
        self.modifyTimeLabel.setFixedWidth(170)
        self.modifyTimeLabel.setObjectName("modifyTimeLabel")
        metaLayout.addWidget(self.modifyTimeLabel)
        self.authorLabel = QLabel(u"作者: ", self)
        self.authorLabel.setObjectName("authorLabel")
        metaLayout.addWidget(self.authorLabel)
        self.authorLineEdit = QLineEdit(self)
        self.authorLineEdit.setFixedWidth(120)
        self.authorLineEdit.setObjectName("authorLineEdit")
        self.authorLineEdit.setPlaceholderText(u"点击输入作者")
        metaLayout.addWidget(self.authorLineEdit)
        self.sourceLabel = QLabel(KindEditor.SOURCE_FORMAT % ("", ""), self)
        self.sourceLabel.setFixedWidth(250)
        self.sourceLabel.setObjectName("sourceLabel")
        self.sourceLabel.linkActivated.connect(self.__openUrl)
        metaLayout.addWidget(self.sourceLabel)

        metaLayout.addStretch()
        self.metaWidget.setLayout(metaLayout)
        self.layout.addWidget(self.metaWidget)

        #编辑器
        self.webView = QWebView(self)
        self.layout.addWidget(self.webView)

        if conf == None:
            self.url = KindEditor.DEFAULT_SERVER
        else:
            self.url = conf.get("server", "basesite", "http://127.0.0.1:9876")

        self.setLayout(self.layout)

        #启动本地HTTP服务
        #runServer("./resources/editor", "127.0.0.1", 9876)


    def __setStyleSheet(self):
        qsspath = "./resources/qss/KindEditor.qss"
        qssfile = QFile(qsspath)
        if qssfile.exists() == False:
            return

        if qssfile.open(QIODevice.ReadOnly) == False:
            return

        self.setStyleSheet(QString(qssfile.readAll()))

    def loadEditor(self):
        self.webView.load(QUrl(self.url + "/examples/default.html"))
        self.connect(self.webView, SIGNAL("loadFinished(bool)"), self.loadFinished)

    def loadFinished(self, finished):
        print "loadFinished"
        doc = self.webView.page().currentFrame().documentElement()
        content = doc.findFirst("body")
        content.setAttribute("style", "margin: 0px")
        self.resizeEvent(None)

        doc.findFirst("div[class=ke-statusbar]").removeFromDocument()

        #self.webView.page().currentFrame().javaScriptWindowObjectCleared.connect(self.addObjectToJs)
        self.addObjectToJs()
        self.btn.clicked.connect(self.testJs)
        self.jsInvokeQt.connect(self.testJs)

    def addObjectToJs(self):
        print "addObjectToJs"
        self.webView.page().currentFrame().addToJavaScriptWindowObject("WeiXin", self)

    def testJs(self):
        print "testJs"
        self.webView.page().currentFrame().evaluateJavaScript("disp_messagebox(\"%s\")" % "hello")

    def resizeEvent(self, e):
        doc = self.webView.page().currentFrame().documentElement()
        content = doc.findFirst("div")
        content.setAttribute("style", "width: %dpx; padding: 0px; height: %dpx" % ((self.width() - 2), (self.height() - 50)))

        content = doc.findFirst("div[class=ke-edit]")
        content.setAttribute("style", "display:block; height: %dpx" % (self.height() ))

        content = doc.findFirst("iframe[class=ke-edit-iframe]")
        content.setAttribute("style", "display:block; width: %dpx;  height: %dpx" % ((self.width() - 2), self.height() - 100))

    def __detailButtonClicked(self):
        bVisible = self.metaWidget.isVisible()
        info = u"详细信息"
        if bVisible == False:
            info = u"隐藏信息"
        self.detailButton.setText(info)
        self.metaWidget.setHidden(bVisible)

    def __openUrl(self, url):
        QDesktopServices.openUrl(QUrl(url))

    def setNote(self, note):
        self.titleLineEdit.setText(note.title)
        self.createTimeLabel.setText(KindEditor.CREATE_TIME_FORMAT % (datetime.fromtimestamp(note.create_time).strftime("%Y-%m-%d")))
        self.modifyTimeLabel.setText(KindEditor.MODIFY_TIME_FORMAT % (datetime.fromtimestamp(note.modify_time).strftime("%Y-%m-%d")))
        self.authorLineEdit.setText(note.author)
        self.sourceLabel.setText(KindEditor.SOURCE_FORMAT % (note.source, note.source))

        print note.content
        self.webView.page().currentFrame().evaluateJavaScript("setHtml(\"%s\")" % note.path)



if __name__ == "__main__":
    app = QApplication(sys.argv)

    wx = KindEditor()
    wx.loadEditor()
    wx.show()

    sys.exit(app.exec_())


