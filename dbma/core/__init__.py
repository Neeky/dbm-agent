
import time
import logging
import argparse
from logging.handlers import RotatingFileHandler

levels = {
    'info': logging.INFO,
    'debug': logging.DEBUG,
    'error': logging.ERROR,
    'warn': logging.WARN
    }
handler = RotatingFileHandler(filename="/tmp/dbm-agent.log", maxBytes=128 * 1024 * 1024, backupCount=8, encoding="utf8")
logging.basicConfig(handlers=[handler], level=logging.INFO, format="[%(asctime)s %(levelname)s] - [%(threadName)s] - [%(pathname)s %(lineno)d line]  ~  %(message)s")
