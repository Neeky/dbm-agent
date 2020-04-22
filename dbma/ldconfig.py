import logging
import subprocess

from . import privileges as prv

logger = logging.getLogger("dbm-agent").getChild(__name__)


def ldconfig():
    """加载 so 文件
    """
    lgr = logging.getLogger("ldconfig")
    lgr.info("start.")
    with prv.sudo("ldconfig"):
        subprocess.run("ldconfig", shell=True)
    lgr.info("complete.")

