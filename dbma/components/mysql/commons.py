# -*- encoding: utf-8 -*-

"""MySQL 组件的公共函数
"""

import re
import logging
import shutil
from pathlib import Path
from dbma.bil.fun import fname
from dbma.bil.cmdexecutor import exe_shell_cmd
from dbma.core import messages
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
    dst_include_dir = Path("/usr/include/") / "mysql-{}".format(get_mysql_version(pkg.name))
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
    
    conf_file = Path("/etc/ld.so.conf.d") / "mysql-{}.conf".format(get_mysql_version(pkg.name))
    if not conf_file.exists():
        with open(conf_file, 'w') as f:
            mysql_lib_dir = pkg_to_basedir(pkg) / "lib/"
            f.write(str(mysql_lib_dir))
            f.write("\n")
            
    exe_shell_cmd("ldconfig")
    
    logging.info(messages.FUN_ENDS.format(fname()))
    
