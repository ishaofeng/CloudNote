#! /usr/bin/python
#encoding=utf-8
#author: fakir

from PyQt4.QtGui import QApplication
from config import *
from log import *
from DBManager import *
from YouDaoCloudService import YouDaoCloudService
from AuthorizeWidget import AuthorizeWidget
from SyncThread import SyncThread
from CloudNote import CloudNote

if __name__ == "__main__":
    app = QApplication([])
    logger = getLogger()

    conf = getConf()

    cloudService = YouDaoCloudService(conf, logger)
    if cloudService.checkAuth() == False:
        logger.debug("服务未认证,用户登陆")
        tokens = cloudService.requestToken()
        print "tokens", tokens
        verifier = AuthorizeWidget.getVerifier(BASE_URL + "/oauth/authorize?oauth_token=" + tokens["token"])
        cloudService.accessToken(tokens["token"], tokens["secret"], verifier)

    db = DBManager(conf, logger)

    cloudNote = CloudNote(cloudService, db, conf, logger)
    cloudNote.show()

    syncThread = SyncThread(cloudNote)
    syncThread.start()

    syncThread.join()


#    resp, content = cloudService.getUser()
#    if resp['status'] == '200':
#        logger.debug("getUser")
#        print content, type(content)
#        db.insertUser(content)
    app.exec_()





