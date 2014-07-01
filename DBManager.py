#! /usr/bin/python
#encoding=utf-8
#author: fakir

from sqlalchemy import *
from sqlalchemy.orm import *
from config import DATABASE_PATH

class DBManager():
    def __init__(self, conf, logger):
        self.conf = conf
        self.logger = logger
        self.engine = create_engine("sqlite:///%s" % DATABASE_PATH, echo=False)
        self.metadata = MetaData(self.engine)

        self.createUserTable()
        self.createNotebookTable()
        self.createNoteTable()

        mapper(User, self.usertable)
        mapper(Note, self.notetable)
        mapper(Notebook, self.notebooktable)

        self.Session = sessionmaker()
        self.Session.configure(bind=self.engine)

    def createSession(self):
        return self.Session()

    def createUserTable(self):
        try:
            self.usertable = Table("user", self.metadata, autoload=True)
        except:
            self.logger.debug("user表不存在, 创建user表")
            self.usertable = Table("user", self.metadata,
                          Column("id", String(48)),
                          Column("user", String(32), primary_key=True),
                          Column("last_login_time", BigInteger()),
                          Column("total_size", BigInteger()),
                          Column("register_time", BigInteger()),
                          Column("default_notebook", String(64)),
                          Column("last_modify_time", BigInteger()),
                          Column("used_size", BigInteger()))
            self.usertable.create()
        else:
            self.logger.debug("user表已经存在")

    def createNotebookTable(self):
        try:
            self.notebooktable = Table("notebook", self.metadata, autoload=True)
        except:
            self.logger.debug("notebook表不存在,创建notebook表")
            self.notebooktable = Table("notebook", self.metadata,
                        Column("path", String(128), primary_key=True),
                        Column("name", String(64)),
                        Column("create_time", BigInteger()),
                        Column("modify_time", BigInteger()),
                        Column("notes_num", Integer()),
                        Column("group", String(32)),
                        Column("sync", Boolean()))
            self.notebooktable.create()
        else:
            self.logger.debug("notebook表已经存在")

    def createNoteTable(self):
        try:
            self.notetable = Table("note", self.metadata, autoload=True)
        except:
            self.notetable = Table("note", self.metadata,
                        Column("path", String(128), primary_key=True),
                        Column("title", String(64)),
                        Column("author", String(32)),
                        Column("summary", String(128)),
                        Column("content", String(256)),
                        Column("source", String(128)),
                        Column("create_time", BigInteger()),
                        Column("modify_time", BigInteger()),
                        Column("size", BigInteger()),
                        Column("sync", Boolean()))
            self.notetable.create()
        else:
            self.logger.debug("note表已经存在")



class User(object):
    pass

class Notebook(object):
    pass

class Note(object):
    pass

