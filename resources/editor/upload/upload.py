#! /usr/bin/python
#encoding=utf-8

from bottle import *
import uuid

app = Bottle()

root="/home/shao/Dropbox/source/test/kindeditor-4.1.7"

@app.post("/upload")
def upload():
    f = request.files["imgFile"]
    t = request.GET["dir"]

    uid = str(uuid.uuid1())
    path = root + "/file/" + uid

    with open(path, "w") as wf:
        wf.write(f.value)

    return "{\"error\":0, \"url\":\"http://127.0.0.1:8080/file/%s\"}"  % uid

@app.get("/<filename:path>")
def staticfile(filename):
    print filename
    return static_file(filename, root=root)



run(app, host="127.0.0.1", port=8080)

