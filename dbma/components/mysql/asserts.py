# -*- coding: utf-8 -*-

"""MySQL 相关的一些断言项
"""

from pathlib import Path
from dbma.core.configs import dbm_agent_config
from dbma.components.mysql.exceptions import (
    MySQLPkgFileNotExistsException,
    MySQLDataDirectoryExists,
    MySQLSystemdFileExists,
    MySQLSystemdFileNotExists,
)


def assert_mysql_install_pkg_exists(pkg: Path = None):
    """
    断言 MySQL 的安装包文件是否存在，如果不存在就报异常

    parameters:
    -----------
    pkg: Path
        MySQL 安装包全路径

    Exceptions:
    -----------
    MySQLPkgFileNotExistsException
    """
    # 如果只是给了一个安装文件的名字，就把默认的前缀补上
    if pkg.is_absolute() and str(pkg).startswith("mysql"):
        pkg = Path("/usr/local/dbm-agent/pkgs/") / pkg

    # 不存在就报异常
    if not pkg.exists():
        raise MySQLPkgFileNotExistsException(
            "mysql install pkg '{}' not exists .".format(str(pkg))
        )


def assert_mysql_datadir_not_exists(port: int = 3306):
    """
    断言对应端口的 MySQL 实例的数据目录存在

    parameters:
    -----------
    port: int
        MySQL 端口号

    Exceptions:
    -----------
    MySQLDataDirectoryExists
    """
    datadir = Path(dbm_agent_config.mysql_datadir_parent) / "{}".format(port)
    if datadir.exists():
        message = "mysql data '{}' directory exists .".format(datadir)
        raise MySQLDataDirectoryExists(message)


def assert_mysql_systemd_file_not_exists(port: int = 3306):
    """
    断言对应端口的 MySQL systemd 配置文件不存在、如果实际的情况与断言不一致就报异常

    parameters:
    -----------
    port: int
        MySQL 端口号

    Exceptions:
    -----------
    MySQLSystemdFileExists
    """
    systemd_file = Path("/usr/lib/systemd/system/mysqld-{}.service".format(port))
    if systemd_file.exists():
        message = "mysql systemd config file '{}' exists.".format(str(systemd_file))
        raise MySQLSystemdFileExists(message)


def assert_mysql_systemd_file_exists(port: int = 3306):
    """
    断言对应端口的 MySQL systemd 配置文件存在、如果实际的情况与断言不一致就报异常

    parameters:
    -----------
    port: int
        MySQL 端口号

    Exceptions:
    -----------
    MySQLSystemdFileExists
    """
    systemd_file = Path("/usr/lib/systemd/system/mysqld-{}.service".format(port))
    if not systemd_file.exists():
        # 如果不存在就要报异常
        message = "mysql systemd config file '{}' exists.".format(str(systemd_file))
        raise MySQLSystemdFileNotExists(message)
