# -*- coding: utf-8 -*-

"""
MySQL 安装配置相关领域
作者: neeky | neeky@live.com
时间: 2023-07-21
"""

from pathlib import Path
from dbma.bil.osuser import MySQLUser
from dbma.core.configs import dbm_agent_config


class MySQLUserMixin(object):
    """
    OS 层面 mysql{port} 用户域
    """

    def __init__(self, port: int):
        self.user = MySQLUser(port)
        self.data_dir_path = Path(dbm_agent_config.mysql_datadir_parent) / str(port)
        self.binlog_dir_path = Path(dbm_agent_config.mysql_binlogdir_parent) / str(port)
        self.backup_dir_path = Path(dbm_agent_config.mysql_backupdir_parent) / str(port)
        self.etc_cnf_path = Path("/etc/my-{}.cnf".format(port))

    def create_os_user(self):
        """
        创建 MySQL 用户
        """
        self.user.create()

    def create_dirs(self):
        """
        创建 MySQL 实例相关的数据目录、日志目录、备份目录
        """
        for path in (self.data_dir_path, self.binlog_dir_path, self.backup_dir_path):
            if not path.exists():
                path.mkdir(parents=True)
                self.user.chown(path)


class MySQLInstaller(MySQLUserMixin):
    """ """

    def __init__(self, port: int = 3306):
        MySQLUserMixin.__init__(self, port)

    def install(self):
        # 0. 检查
        # 1. 创建操作系统层面的用户
        self.create_os_user()
        # 2. 创建目录
        self.create_dirs()
        pass


class MySQLSourceInstaller(MySQLInstaller):
    pass
