#! /usr/bin/python
#encoding=utf-8
#author: fakir


from config import APP_PATH, BASE_URL
from multiprocessing import Process
from PyQt4.QtCore import QObject
from DBManager import User, Note, Notebook
import os
import re

class SyncThread(Process, QObject):
    def __init__(self, cloudNote):
        Process.__init__(self)
        QObject.__init__(self)

        self.cloudService = cloudNote.cloudService
        self.db = cloudNote.db
        self.conf = cloudNote.conf
        self.logger = cloudNote.logger
        self.cache = cloudNote.cache

        self.isRunning = True
        self.basepath = "%s/data" % APP_PATH
        self.resourcebaseurl = "%s/yws/open/resource/download/" % BASE_URL
        if os.path.exists(self.basepath)  == False:
            os.mkdir(self.basepath)

    def __writeFile(self, path, content):
        with open(path, "w") as f:
            f.write(content)

    def __checkAndSaveResourcesFile(self, path, content):
        resources = re.findall('''<img[^>]+src=\"(%s.+?)?\"[^>]+>''' % self.resourcebaseurl, content)
        for resource in resources:
            print "resource: ", resource
            resp, data = self.cloudService.downloadResource(resource)
            if resp["status"] == "200":
                rpath = resource.replace(self.resourcebaseurl, "")
                items = rpath.split("/")
                testpath = self.basepath + path
                for i, item in enumerate(items):
                    print "testpath: ", testpath
                    testpath += "/" + items[i]
                    if i == (len(items) -1):
                        self.__writeFile(testpath, data)
                    else:
                        if os.path.exists(testpath) == False:
                            os.mkdir(testpath)
                content = content.replace(resource, "/note" + path + "/" + rpath)

        return content

    def __updateNote(self, session, note):
        resp, content = self.cloudService.getNote(note)
        if resp["status"] != "200":
            return ;

        note = session.query(Note).filter_by(path=note).first()
        notepath = self.basepath + content["path"]
        notecontentpath = self.basepath + content["path"] + "/index.html"
        notecontent = content["content"]
        print "content: ", content
        if note == None:
            note = Note()
            note.path = content["path"]
            note.title = content["title"]
            note.author = content["author"]
            note.summary = content["summary"]
            note.content = notecontentpath
            note.source = content["source"]
            note.create_time = content["create_time"]
            note.modify_time = content["modify_time"]
            note.size = content["size"]
            note.sync = True

            session.add(note)
            session.flush()
            session.commit()

            os.mkdir(self.basepath + note.path)
        elif note.modify_time < content["modify_time"]:
            note.title = content["title"]
            note.author = content["author"]
            note.summary = content["summary"]
            note.content = notecontentpath
            note.source = content["source"]
            note.modify_time = content["modify_time"]
            note.size = content["size"]
            note.sync = True

            session.commit()

        notecontent = self.__checkAndSaveResourcesFile(content["path"], notecontent)
        self.__writeFile(notecontentpath, notecontent)



    def __updateNotebook(self, session, notebook):
        resp, content = self.cloudService.listNotebook(notebook)
        if resp["status"] != "200":
            return ;
        print content

        for note in content:
            self.__updateNote(session, note)

    def __updateNotebooks(self, session):
        resp, content = self.cloudService.getAllNotebook()
        if resp["status"] != "200":
            return ;

        newNotebooks = {}
        for notebook in content:
            newNotebooks[notebook["path"]] = notebook

        notebooks = list(session.query(Notebook))
        for notebook in notebooks:
            path = notebook.path
            if newNotebooks.contains(path) and \
                newNotebooks[path]["last_modify_time"] > notebook.last_modify_time:
                self.__updateNotebook(session, path)
            elif newNotebooks.contain(path) == False:
                session.delete(notebook)

            del newNotebooks[path]

        #将新添加的笔记本加入到数据库
        for notebook in newNotebooks.values():
            self.logger.debug("add new")
            os.mkdir(self.basepath + notebook["path"])
            self.__updateNotebook(session, notebook["path"])
            n = Notebook()
            n.path = notebook["path"]
            n.name = notebook["name"]
            n.create_time = notebook["create_time"]
            n.modify_time = notebook["modify_time"]
            n.notes_num = notebook["notes_num"]
            n.group = notebook["group"]
            n.sync = False

            session.add(n)

        session.flush()
        session.commit()

    def run(self):
        session = self.db.createSession()
        while self.isRunning:
            #请求用户信息
            resp, content = self.cloudService.getUser()
            while resp["status"] != "200":
                resp, content = self.cloudService.getUser()

            user = content["user"]
            self.cache["user"] = user

            u = session.query(User).filter_by(user=user).first()
            if u == None:
                self.logger.debug("add user %s" % user)
                u = User()
                u.id = content["id"]
                u.user = content["user"]
                u.register_time = content["register_time"]
                session.add(u)
                session.flush()
                session.commit()

            last_modify_time = u.last_modify_time

            u.last_modify_time = content["last_modify_time"]
            u.used_size = content["used_size"]
            u.default_notebook = content["default_notebook"]
            u.last_login_time = content["last_login_time"]
            u.total_size = content["total_size"]
            session.commit()

            #时间戳发生变化检查更新
            if last_modify_time < u.last_modify_time:
                self.logger.debug("发生新变化")
                self.__updateNotebooks(session)

            self.isRunning = False









if __name__ == "__main__":
    t  = SyncThread(None, None, None)
    t.start()
