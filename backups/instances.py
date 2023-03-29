"""实现 MySQL 实例的创建功能
"""
import os
import random
import logging
from .softinstall import MySQLBinaryInstall

logger = logging.getLogger("dbm-agent").getChild(__name__)


class MySQLInstanceCreater(object):
    """实现 MySQL 实例的初始化功能。
    """
    logger = logger.getChild("MySQLInstanceCreater")
    data_dir = "/database/mysql/data/"
    binlog_dir = "/binlog/mysql/binlog/"
    backup_dir = "/backup/mysql/backup/"

    def __init__(self, pkg="mysql-8.0.19-linux-glibc2.12-x86_64.tar.xz", port=3306, mem=128):
        """
        """
        logger = self.logger.getChild("__init__")
        logger.ifno("start.")

        # 根据 port 和 mem 给各个参数一个基本值
        self.server_id = random.randint(1024, 9999)
        self.port = port
        self.mysqlx_port = self.port * 10
        self.admin_port = self.mysqlx_port + 2
        self.user = f"mysql{port}"
        self.socket = f"/tmp/mysql-{self.port}.sock"
        self.mysqlx_socket = f"/tmp/mysqlx-{self.port}.sock"
        self.pid = f"/tmp/mysql-{self.port}.pid"
        self.basedir = MySQLBinaryInstall(pkg=pkg).mysql_base_dir
        self.datadir = os.path.join(self.data_dir, str(self.port))
        self.log_bin = os.path.join(self.binlog_dir, str(self.port))
        self.bind_address = '*'
        self.admin_address = "127.0.0.1"

        # 非参数
        self.backup_dir = os.path.join(
            self.__class__.backup_dir, str(self.port))
