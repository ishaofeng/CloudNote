#! /usr/bin/python
#coding=utf-8
#author: fakir

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import oauth2 as oauth
from AuthorizeWidget import AuthorizeWidget
from config import *
import json
from StringIO import StringIO
import mimetools
import mimetypes
import os

class YouDaoCloudService():
    def __init__(self, conf, logger):
        self.conf = conf
        self.logger = logger
        self.oauth_consumer_token = self.conf.get("oauth", "oauth_consumer_token")
        self.oauth_consumer_secret = self.conf.get("oauth", "oauth_consumer_secret")
        self.consumer = oauth.Consumer(key=self.oauth_consumer_token, secret=self.oauth_consumer_secret)

        self.isAuth = True

        #获取认证信息
        try:
            self.oauth_token = self.conf.get("oauth", "oauth_token")
            self.oauth_secret = self.conf.get("oauth", "oauth_secret")
            self.token = oauth.Token(self.oauth_token, self.oauth_secret)
            self.client = oauth.Client(self.consumer, token=self.token)
        except Exception, e:
            print "exception "
            self.oauth_token = ""
            self.oauth_secret = ""
            self.isAuth = False


    #检测是否已经认证登陆
    def checkAuth(self):
        return self.isAuth

    def __splitToken(self, content):
        items = content.split("&")
        return {"token": items[0].split("=")[1], "secret": items[1].split("=")[1]}

    def requestToken(self):
        client = oauth.Client(self.consumer)
        resp, content = client.request(BASE_URL + "/oauth/request_token", "GET", headers={"oauth_callback": "oob"})
        return self.__splitToken(content)

    def accessToken(self, request_token, request_secret, verifier):
        self.token = oauth.Token(request_token, request_secret)
        self.token.set_verifier(verifier=verifier)

        client = oauth.Client(self.consumer, token = self.token)
        resp, content = client.request(BASE_URL + "/oauth/access_token", "GET")

        #将accessToken更新到配置文件
        print "content: ", content
        result = self.__splitToken(content)
        self.oauth_token = result["token"]
        self.oauth_secret = result["secret"]
        self.token = oauth.Token(self.oauth_token, self.oauth_secret)
        self.client = oauth.Client(self.consumer, token=self.token)
        self.conf.set("oauth", "oauth_token", self.oauth_token)
        self.conf.set("oauth", "oauth_secret", self.oauth_secret)
        saveConf(self.conf)

        return {"token": self.oauth_token, "secret": self.oauth_secret}

    def getUser(self):
        resp, content = self.client.request(BASE_URL + "/yws/open/user/get.json", "GET")

        return resp, json.loads(content)

    def getAllNotebook(self):
        resp, content = self.client.request(BASE_URL + "/yws/open/notebook/all.json",
                                "POST", headers={"Content-Type": "application/x-www-form-urlencoded"})
        return resp, json.loads(content)

    def listNotebook(self, notebook):
        resp, content = self.client.request(BASE_URL + "/yws/open/notebook/list.json",
                                "POST", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=("notebook=%s" % (notebook)))
        return resp, json.loads(content)

    def createNotebook(self, notebook):
        resp, content = self.client.request(BASE_URL + "/yws/open/notebook/create.json",
                                "POST", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=("name=%s" % (notebook)))
        return resp, json.loads(content)

    def deleteNotebook(self, notebook):
        resp, content = self.client.request(BASE_URL + "/yws/open/notebook/delete.json",
                                "POST", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=("notebook=%s" % (notebook)))
        return resp, json.loads(content)

    def createNote(self, notebook, content, title="", author="", source=""):
        items = {"notebook": notebook, "content": content, "title": title, "author": author, "source": source}
        boundary, body = self.multipart_encode(items, {})

        resp, content = self.client.request(BASE_URL + "/yws/open/note/create.json",
                            "POST", headers={"Content-Type": "multipart/form-data; boundary=%s" % boundary}, body=body)

        return resp, json.loads(content)

    def getNote(self, path):
        resp, content = self.client.request(BASE_URL + "/yws/open/note/get.json",
                                "POST", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=("path=%s" % (path)))
        return resp, json.loads(content)

    def updateNote(self, path, content, title="", author="", source=""):
        items = {"path": path, "content": content, "title": title, "author": author, "source": source}
        boundary, body = self.multipart_encode(items, {})

        resp, content = self.client.request(BASE_URL + "/yws/open/note/update.json",
                            "POST", headers={"Content-Type": "multipart/form-data; boundary=%s" % boundary}, body=body)

        return resp, json.loads(content)

    def moveNote(self, path, notebook):
        resp, content = self.client.request(BASE_URL + "/yws/open/note/move.json",
                                "POST", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=("path=%s&notebook=%s" % (path, notebook)))
        return resp, json.loads(content)

    def deleteNote(self, path):
        resp, content = self.client.request(BASE_URL + "/yws/open/note/delete.json",
                                "POST", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=("path=%s" % (path)))
        return resp, json.loads(content)

    def publishNote(self, path):
        resp, content = self.client.request(BASE_URL + "/yws/open/share/publish.json",
                                "POST", headers={"Content-Type": "application/x-www-form-urlencoded"}, body=("path=%s" % (path)))
        return resp, json.loads(content)

    def uploadResource(self, file):
        files = {"file": open(file, "r")}
        boundary, body = self.multipart_encode({}, files)

        resp, content = self.client.request(BASE_URL + "/yws/open/resource/upload.json",
                            "POST", headers={"Content-Type": "multipart/form-data; boundary=%s" % boundary}, body=body)

        return resp, json.loads(content)

    def downloadResource(self, url):
        resp, content = self.client.request(url, "GET")
        return resp, content

    def multipart_encode(self, vars, files, boundary = None, buf = None):
        if boundary is None:
            boundary = mimetools.choose_boundary()
        if buf is None:
            buf = StringIO()

        for (key, value) in vars.items():
            buf.write('--%s\r\n' % boundary)
            buf.write('Content-Disposition: form-data; name="%s"' % key)
            buf.write('\r\n\r\n' + value + '\r\n')

        for (key, fd) in files.items():
            file_size = os.fstat(fd.fileno()).st_size
            filename = fd.name.split('/')[-1]
            contenttype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            buf.write('--%s\r\n' % boundary)
            buf.write('Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (key, filename))
            buf.write('Content-Type: %s\r\n' % contenttype)
            # buffer += 'Content-Length: %s\r\n' % file_size
            fd.seek(0)
            buf.write('\r\n' + fd.read() + '\r\n')
        buf.write('--' + boundary + '--\r\n\r\n')
        buf = buf.getvalue()

        return boundary, buf

if __name__ == "__main__":
    conf = getConf()
    service = YouDaoCloudService(conf, None)
    print service.isAuth
    if service.checkAuth() == False:
        tokens =  service.requestToken()

        verifier = AuthorizeWidget.getVerifier(BASE_URL + "/oauth/authorize?oauth_token=" + tokens["token"])
        print "verifier: ", verifier

        print "token: ", service.accessToken(tokens["token"], tokens["secret"], verifier)
    else:
        print "have token"

    print service.getUser()
    resp, notebooks = service.getAllNotebook()
    print notebooks
#    print notebooks[0]["path"]
    resp, items = service.listNotebook(notebooks[3]["path"])
    print items
    #print service.createNotebook("shaotest")
    shaotest = "/8F2A32B3EA534E5C995F2A2896A93191"
    resp, items = service.listNotebook(shaotest)
    #print service.createNote(shaotest, "hello workd", title="test")
#
    print service.getNote((items)[0])
#    print service.publishNote((items)[0])
#    print service.uploadResource("oauth.py")


