#! /usr/bin/python
#encoding=utf-8

from bottle import *
import threading
import uuid

app = Bottle()

basedir=""
basesite=""
cloudService=""

@app.post("/upload")
def upload():
    f = request.files["imgFile"]
    t = request.GET["dir"]

    uid = str(uuid.uuid1())
    path = basedir + "/file/" + uid

    with open(path, "w") as wf:
        wf.write(f.value)

    return "{\"error\":0, \"url\":\"%s/file/%s\"}"  % (basesite, uid)

@app.post("/note/save")
def note_save():
    content = request.body
    images = re.findall('''<img[^>]+src=\"(%s.+?)?\"[^>]+>''' % basesite, content)
    for image in images:
        localimagepath = basedir + image.replace(basesite + "/file", "")
        resp, content = cloudService.uploadResource(localimagepath)


@app.get("/<filename:path>")
def staticfile(filename):
    print filename
    return static_file(filename, root=basedir)


def runServer(root, service, host="127.0.0.1", port=9876):
    global basedir
    global basesite
    global cloudService

    basedir = root
    basesite = "http://%s:%d" % (host, port)
    cloudService = service

    #thread = threading.Thread(target=run, args=(app, host, port))
    run(app, host=host, port=port)
    return thread

if __name__ == "__main__":
    runServer("./resources/editor")

