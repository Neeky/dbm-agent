# -*- encoding: utf-8 -*-

"""MySQL 组件的公共函数
"""

import re
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


    
