"""
实现 mysqldump 、mysqlbackup 、extrabackup 的备份
"""

# (c) 2019, LeXing Jiang <neeky@live.com 1721900707@qq.com https://www.sqlpy.com/>
# Copyright: (c) 2019, dbm Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import re
import logging
from datetime import datetime
from configparser import ConfigParser

from . import messages
from . import errors
from . import checkings
from . import common
from .dbmacnf import cnf

logger = logging.getLogger('dbm-agent').getChild(__name__)


class BaseBackuper(object):
    """
    所有备份类的基类
    """
    logger = logging.getLogger("BaseBackuper")

    default_options = None

    def __init__(self, host="127.0.0.1", port=3306, mysql_user="", mysql_password=""):
        """

        """
        logger = self.logger.getChild("__init__")
        self.host = host
        self.port = port
        self.backup_user = mysql_user
        self.backup_password = mysql_password
        self.backupdir = f"/backup/mysql/backup/{self.port}"

        # 备份集目录(/backup/mysql/backup/2020-1/)
        # 年，当前是年内的第几周，周内的第几日

        self.now = datetime.now()
        year, week, day = self.now.isocalendar()
        self.year = year
        self.week = week
        self.day = day
        # /backup/mysql/backup/2020-1/
        self.backupsets = os.path.join(
            self.backupdir, f"{self.year}-{self.week}/")

        logger.debug(messages.CURRENT_DATETIME.format(self.now.isoformat()))
        logger.info(messages.BACKUPSETS_DIRECTORY.format(self.backupsets))

    def backup(self):
        """
        实现备份相关的逻辑
        """
        raise NotImplementedError(
            messages.NOTIMPLEMENTEDFUNCTION.format("backup"))

    def read_options(self):
        """
        从 /usr/local/dbm-agent/etc/dbma.cnf 中读取配置项、这样每次备份都可以读到最新的配置项、不缓存。
        """
        raise NotImplementedError(
            messages.NOTIMPLEMENTEDFUNCTION.format("read_options"))


class MySQLDumpBackuper(BaseBackuper):
    """
    实现 mysqldump 备份的相关逻辑
    """

    default_options = {
        ''
    }

    def read_options(self):
        """
        读取配置文件
        """
        logger = self.logger.getChild("read_options")
        config_file_path = os.path.join(cnf.base_dir, cnf.config_file)

        # 从 /usr/local/dbm-agent/etc/dbma.cnf 的 mysqldump 中读取配置项
        logger.debug(
            messages.READ_CONFIG_OPTION_FROM_FILE.format(config_file_path))

        parser = ConfigParser()
        parser.read(config_file_path)

        # 检查 mysqldump 这个配置结点是否在配置文件中
        if 'mysqldump' not in parser:

            # 如果没有在
            pass
