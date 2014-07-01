#! /usr/bin/python
#encoding=utf-8
#author: fakir

import oauth2 as oauth
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from config import *

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *
from PyQt4.QtNetwork import *

class AuthorizeWidget(QDialog):
    def __init__(self, authorize_url, parent=None):
        QDialog.__init__(self, parent)
        self.authorize_url = authorize_url

        self.setWindowTitle(APP_NAME)

        self.layout = QHBoxLayout()
        self.webView = QWebView(self)
        self.layout.addWidget(self.webView)
        self.layout.setSpacing(0)
        self.layout.setMargin(0)

        self.setLayout(self.layout)

        self.setFixedWidth(290)
        self.setFixedHeight(290)

        self.verifier = ""

    def loadAuthorize(self):
        self.webView.load(QUrl(self.authorize_url))
        self.connect(self.webView, SIGNAL("loadFinished(bool)"), self.loadFinished)

    def loadFinished(self, finished):
        frame = self.webView.page().currentFrame()
        url = frame.url().toString()
        print "url: ", url

        doc = frame.documentElement()

        if url.startsWith("http://account.youdao.com/login"):    #初始登陆界面
            doc.findFirst("div[id=t]").removeFromDocument()
            doc.findFirst("div[id=b]").removeFromDocument()
            doc.findFirst("div[class=login_left]").removeFromDocument()

            content =  doc.findFirst("div[id=login]")
            content.setStyleProperty("position", "fixed")
            content.setStyleProperty("width", "100px")
            content.setStyleProperty("padding", "0px")

            login = doc.findFirst("div[class=login_right]")
            login.setStyleProperty("float", "none")
        elif url.startsWith("http://note.youdao.com/oauth/authorize_handler"):       #登陆成功确认界面
            doc.findFirst("button[id=auth-btn]").evaluateJavaScript("this.click()")
        elif url == "http://note.youdao.com/oauth/authorize":
            text = doc.toPlainText()
            print "text: ", text
            reg = QRegExp("[0-9]{4,}")
            pos = reg.indexIn(text, 0)
            if pos != -1:
                self.verifier = str(reg.cap(0))
                self.close()

    @staticmethod
    def getVerifier(url):
        w = AuthorizeWidget(url)
        w.loadAuthorize()
        w.exec_()

        return w.verifier
