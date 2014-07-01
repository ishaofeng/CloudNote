#! /usr/bin/python
#encoding=utf-8
#author: fakir

import os
import ConfigParser

APP_NAME = "CloudNote"
APP_PATH = "%s/.%s" % (os.path.expanduser("~"), APP_NAME)
CONFIG_FILE = "%s.ini" % APP_NAME
CONFIG_PATH = "%s/%s" % (APP_PATH, CONFIG_FILE)
DATABASE_PATH = "%s/%s.db" % (APP_PATH, APP_NAME)
LOG_PATH = "%s/%s.log" % (APP_PATH, APP_NAME)

BASE_URL = "http://note.youdao.com"

#获取配置文件
def getConf():
    if os.path.exists(APP_PATH) == False:
        os.mkdir(APP_PATH)

    if os.path.exists(CONFIG_PATH) == False:
        os.system("cp %s %s" % (CONFIG_FILE, CONFIG_PATH))

    conf = ConfigParser.ConfigParser()
    conf.read(CONFIG_PATH)

    return conf

#保存配置文件
def saveConf(conf):
    if os.path.exists(APP_PATH) == False:
        os.mkdir(APP_PATH)

    conf.write(open(CONFIG_PATH, "w"))


#测试
if __name__ == "__main__":
    conf = getConf()
    print conf.get("oauth", "oauth_consumer_token")
    print conf.get("oauth", "oauth_consumer_secret")

    print conf.get("oauth", "a")
