# -*- encoding: utf-8 -*-

"""MySQL 组件的公共函数
"""

import re
import logging
import shutil
import contextlib
import mysql.connector
from pathlib import Path
from dbma.bil.fun import fname
from dbma.core import messages
from dbma.bil.cmdexecutor import exe_shell_cmd
from dbma.core.configs import dbm_agent_config


default_pkg = Path(
    "/usr/local/dbm-agent/pkgs/mysql-{}-linux-glibc2.12-x86_64.tar.xz".format(
        dbm_agent_config.mysql_default_version
    )
)


def get_mysql_version(pkg_name: str = None):
    """根据 pkg_name 的值，提取 MySQL 的版本号。

    Paramters:
    ----------
    pkg_name: str
        MySQL 安装包的名字 et: mysql-8.0.31-linux-glibc2.12-x86_64.tar.xz

    Return:
    -------
    str | None
    """
    p = re.compile("mysql-(?P<version>\d{1,1}.\d{1,1}.\d{1,2})-linux-glibc")
    if (m := p.match(pkg_name)) and m is not None:
        return m.group("version")
    # 异常场景，目前还不清楚最理想的处理方式
    return None


def pkg_to_basedir(pkg: Path = default_pkg):
    """根据 pkg 的名字计算 basedir 的名字

    Parameter:
    ----------
    pkg: Path
        MySQL 安装包的全路径

    Return:
    -------
        Path
    """
    return Path("/usr/local") / (pkg.name.replace(".tar.gz", "").replace(".tar.xz", ""))


@contextlib.contextmanager
def dbma_mysql_cnx(
    port: int = 3306,
    user: str = dbm_agent_config.mysql_dbma_user,
    password: str = dbm_agent_config.mysql_dbma_password,
):
    """建立到本地 MySQL 结点的短连接, 并返回 cursor 对象, 当连接遇到异常的时候返回 None .

    Parameters:
    -----------
    port: int
        MySQL 端口号

    user: str
        连接 MySQL 的用户名

    password: str
        连接 MySQL 的用户密码

    Return:
    -------
    cursor
    """
    cnx = None
    cursor = None
    host = "127.0.0.1"
    logging.info("dbma_mysql_cnx: connect to {}:{} .".format(host, port))
    try:
        # 连接数据库并返回游标
        cnx = mysql.connector.connect(
            host=host, port=port, user=user, password=password, autocommit=True
        )
        cursor = cnx.cursor()
        yield cursor
    except mysql.connector.errors.Error as err:
        # 连接异常的时候返回 None
        logging.error("dbma_mysql_cnx: can't connect to {}:{}".format(host, port))
        yield None
    finally:
        # 资源回收
        try:
            if cursor is not None:
                cursor.close()
            if cnx is not None:
                cnx.close()
        except (mysql.connector.errors.Error, Exception) as err:
            # 如果 cursor 的接收缓冲区还有内容没有读的话，cursor.close() 会报异常 mysql.connector.errors.InternalError: Unread result found
            logging.info("dbma_mysql_cnx: close cnx got error '{}' .".format(err))


def export_cmds_to_path(basedir: Path = None):
    """根据 basedir 设置 PATH 环境变量"""
    # 读出所有的行
    with open("/etc/profile") as f:
        lines = [line for line in f]

    # 检查是否已经导出了
    export_str = "export PATH={}/bin:$PATH\n".format(basedir)
    if export_str in lines:
        logging.info("has exported.")
        return

    # 如果没有导出就导出
    with open("/etc/profile", "a") as f:
        last_line = lines[-1]
        if not last_line.endswith("\n"):
            # 说明最后一行没有换行，这个情况下先加上换行
            f.write("\n")
        f.write(export_str + "\n")


def export_header_files(pkg: str = None):
    """导出头文件

    Parameters:
    -----------
    pkg: str
        MySQL 安装包全路径

    Return:
    -------

    """
    logging.info(messages.FUN_STARTS.format(fname()))

    # 检查是否已经导出过了
    dst_include_dir = Path("/usr/include/") / "mysql-{}".format(
        get_mysql_version(pkg.name)
    )
    logging.info("dst_include_dir = mysql-{}".format(dst_include_dir))
    if dst_include_dir.exists():
        # 执行到这里说明已经导出过了
        logging.info("dst-incluce-dir '{}' exists. ".format(dst_include_dir))
        logging.info(messages.FUN_ENDS.format(fname()))
        return

    src_include_dir = Path(pkg_to_basedir(pkg)) / "include"
    logging.info("src_include_dir = {}".format(src_include_dir))

    # 复制 include 目录
    shutil.copytree(src_include_dir, dst_include_dir)

    # 结束
    logging.info(messages.FUN_ENDS.format(fname()))


def export_so_files(pkg: Path = None):
    """导出 so 文件

    Parameters:
    -----------
    pkg: str
        MySQL 安装包的大小

    """
    logging.info(messages.FUN_STARTS.format(fname()))

    conf_file = Path("/etc/ld.so.conf.d") / "mysql-{}.conf".format(
        get_mysql_version(pkg.name)
    )
    if not conf_file.exists():
        with open(conf_file, "w") as f:
            mysql_lib_dir = pkg_to_basedir(pkg) / "lib/"
            f.write(str(mysql_lib_dir))
            f.write("\n")

    exe_shell_cmd("ldconfig")

    logging.info(messages.FUN_ENDS.format(fname()))


def make_mysql_writable(port: int = 3306):
    """把结点设置为可写
    Parameters:
    -----------
    port: int
        MySQL 端口号

    Return
    ------
    None
    """
    logging.info(messages.FUN_STARTS.format(fname()))

    with dbma_mysql_cnx(port) as cursor:
        sql = "set @@global.read_only=OFF; set @@global.super_read_only=OFF;"
        cursor.execute(sql)
        logging.info("make mysql instance 127.0.0.1:{} writable .".format(port))
        logging.info("sql = {}".format(cursor.statement))
    logging.info(messages.FUN_ENDS.format(fname()))
