#! /usr/bin/python
#encoding=utf-8
#author: fakir

from config import LOG_PATH, APP_NAME
import logging
import sys



def getLogger():
    logger = logging.getLogger(APP_NAME)

    formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)

    file_handler = logging.FileHandler(LOG_PATH)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    logger.setLevel(logging.DEBUG)
    return logger


if __name__ == "__main__":
    logger = getLogger()
    logger.fatal("hello")
