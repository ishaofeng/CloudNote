#! /usr/bin/python
#encoding=utf-8
#author: fakir

from config import *
import sqlite3


class DBManager():
    def __init__(self, logger):
        self.logger = logger
        self.__initDatabase()

    #初始化数据库
    def __initDatabase(self):
        self.dbcon = sqlite3.connect(DATABASE_PATH)
        cu = self.dbcon.cursor()

        CHECK_TABLE_FORMAT = "select count(*) from sqlite_master where type='table' and name='%s'"

        cu.execute(CHECK_TABLE_FORMAT % "user")
        count = int(cu.fetchall()[0][0])
        if count == 0:
            self.logger.debug("创建数据表 user")
            cu.execute("""create table user(
                user varchar(24),
                total_size bigint,
                used_size bigint,
                register_time bigint,
                last_login_time bigint,
                last_modify_time bigint,
                default_notebook varchar(24)
            )""")

        cu.execute(CHECK_TABLE_FORMAT % "notebook")
        count = int(cu.fetchall()[0][0])
        if count == 0:
            self.logger.debug("创建数据表 notebook")
            cu.execute("""create table notebook(
                path varchar(64) primary key,
                name varchar(64),
                notes_num varchar(8),
                create_time varchar(24),
                modify_time varchar(24),
                sync boolean
            )""")
        cu.execute(CHECK_TABLE_FORMAT % "note")
        count = int(cu.fetchall()[0][0])
        if count == 0:
            self.logger.debug("创建数据表 note")
            cu.execute("""create table note(
                path varchar(128) primary key,
                title varchar(64),
                source varchar(64),
                size varchar(24),
                create_time varchar(24),
                modify_time varchar(24),
                content varchar(128)
            )""")

    def commit(self):
        self.dbcon.commit()

    #插入一个用户
    def insertUser(self, args):
        self.logger.debug("insertUser" )
        cu = self.dbcon.cursor()
        cu.execute("""insert into user values('%(user)s',
                    '%(total_size)ld', '%(used_size)ld',
                    %(register_time)ld, %(last_login_time)ld,
                    %(last_modify_time)ld, '%(default_notebook)s')""" % args)
        self.dbcon.commit()

    #更新一个用户
    def updateUser(self, args):
        self.logger.debug("updateUser" )
        cu = self.dbcon.cursor()
        cu.execute("""update table user set user='%(user)s',
                    '%(total_size)ld', '%(used_size)ld',
                    %(register_time)ld, %(last_login_time)ld,
                    %(last_modify_time)ld, '%(default_notebook)s')""" % args)
        self.dbcon.commit()


    #插入笔记本
    def insertNotebook(self, args):
        self.logger.debug("insertNotebook")
        cu = self.dbcon.cursor()
        cu.execute("""insert into user values('%(path)s',
                    '%(name)s', %(notes_num)d, '%(create_time)s',
                    '%(modify_time)s', %(sync)s)""" % args)
        self.dbcon.commit()



