# -*- encoding: utf-8 -*-

"""MySQL 组件的公共函数
"""

import re
import logging
from pathlib import Path
from dbma.core.configs import dbm_agent_config


default_pkg = Path("/usr/local/dbm-agent/pkgs/mysql-{}-linux-glibc2.12-x86_64.tar.xz".format(
    dbm_agent_config.mysql_default_version))


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
    return Path("/usr/local") / (pkg.name.replace('.tar.gz', '').replace('.tar.xz', ''))


def export_cmds_to_path(basedir: Path = None):
    """根据 basedir 设置 PATH 环境变量
    """
    # 读出所有的行
    with open("/etc/profile") as f:
        lines = [line for line in f]
    
    # 检查是否已经导出了
    export_str = "export PATH={}/bin:$PATH".format(basedir)
    if export_str in lines:
        logging.info("has exported.")
        return
    
    # 如果没有导出就导出
    with open("/etc/profile", 'a') as f:
        last_line = lines[-1]
        if not last_line.endswith("\n"):
            # 说明最后一行没有换行，这个情况下先加上换行
            f.write("\n")
        f.write(export_str + "\n")