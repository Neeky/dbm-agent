# -*- encoding: utf-8 -*-

"""MySQL 安装相关的逻辑实现

作者: 蒋乐兴|neeky@live.com
时间: 2023-03
"""

import os
import shutil
import tarfile
import logging
from pathlib import Path
from datetime import datetime
from dbma.bil.osuser import MySQLUser
from dbma.bil.cmdexecutor import exe_shell_cmd
from dbma.core.configs import dbm_agent_config
from dbma.components.mysql.config import MySQLConfig
from dbma.components.mysql.exceptions import MySQLSystemdFileNotExists
from dbma.components.mysql.exceptions import MySQLPkgFileNotExistsException
from dbma.components.mysql.exceptions import InstanceHasBeenInstalledException


default_pkg = Path("/usr/local/dbm-agent/pkgs/mysql-{}-linux-glibc2.12-x86_64.tar.xz".format(
    dbm_agent_config.mysql_default_version))


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


def checks_for_install(port: int = 3306, pkg: Path = default_pkg):
    """MySQL 安装前的检查

    Parameters:
    -----------
    port: int
        MySQL 端口

    pkg: Path
        MySQL 安装包的全路径

    Return:
    -------
    None

    Exceptions:
    ----------
    MySQLPkgFileNotExistsException

    InstanceHasBeenInstalledException

    """
    # 检查安装包是否存在
    logging.info("check for pkg file exists or not .")
    if not pkg.exists():
        logging.warn("pkg file exists or not .")
        raise MySQLPkgFileNotExistsException(pkg)

    # 检查给定的实例是不是已经安装过了
    logging.info("check {} is installed or not.".format(port))
    datadir = Path(dbm_agent_config.mysql_datadir_parent) / "{}".format(port)
    if datadir.exists():
        logging.warn("instance {} has been installed.".format(port))
        raise InstanceHasBeenInstalledException(str(port))


def check_mysql_systemd_exists(port: int = 3306):
    """检查 mysql 的 systemd 配置文件是否存在

    Paramters:
    ----------
    port: int
        MySQL 端口号

    Returns:
    --------
    None

    Exceptions:
    -----------
    MySQLSystemdFileNotExists
    """
    logging.info("starts check mysql systemd exists 'mysqld-{}' ".format(port))

    systemd_file = Path("/usr/lib/systemd/system/") / \
        "mysqld-{}.service".format(port)
    if not systemd_file.exists():
        logging.error("systemd config file '{systemd_file}' not exists .")
        raise MySQLSystemdFileNotExists(systemd_file)

    logging.info("ends check mysql systemd exists 'mysqld-{}' ".format(port))


def enable_systemd_for_mysql(port: int = 3306):
    """启用 systemd 服务

    Parameters:
    -----------
    port: int
        MySQL 端口号

    Return:
    -------
    None

    Exceptions:
    -----------
    MySQLSystemdFileNotExists
    """
    # 如果 systemd 配置文件不存在就报异常
    logging.info("start enable mysql systemd .")
    try:
        check_mysql_systemd_exists(port)
        # 没有报异常，说明 systemd 配置存在
        # 执行 enable 操作
        eanble_cmd = "systemctl enable mysqld-{}".format(port)
        logging.info("execute '{}' ".format(eanble_cmd))
        exe_shell_cmd(eanble_cmd)
    except MySQLSystemdFileNotExists as err:
        raise err
    logging.info("ends enable systemd '{}' ".format(port))


def disable_systemd_for_mysql(port: int = 3306):
    """禁用 systemd 服务

    Parameters:
    -----------
    port: int
        MySQL 端口号

    Return:
    -------
    None

    Exceptions:
    -----------
    MySQLSystemdFileNotExists
    """
    # 如果 systemd 配置文件不存在就报异常
    logging.info("start disable mysql systemd .")
    try:
        check_mysql_systemd_exists(port)
        # 没有报异常，说明 systemd 配置存在
        # 执行 enable 操作
        disable_cmd = "systemctl disable mysqld-{}".format(port)
        logging.info("execute '{}' ".format(disable_cmd))
        exe_shell_cmd(disable_cmd)
    except MySQLSystemdFileNotExists as err:
        raise err
    logging.info("ends disable systemd '{}' ".format(port))


def start_mysql(port: int = 3306):
    """启动 MySQL 数据库

    Parameter:
    ----------
    port: int
        MySQL 端口号

    Returns:
    -------
    None

    Exceptions:
    -----------
    MySQLSystemdFileNotExists
    """
    # 如果 systemd 配置文件不存在就报异常
    logging.info("starts start mysql .")
    try:
        check_mysql_systemd_exists(port)
        # 没有报异常，说明 systemd 配置存在
        # 执行 start 操作
        start_cmd = "systemctl start mysqld-{}".format(port)
        logging.info("execute '{}' ".format(start_cmd))
        exe_shell_cmd(start_cmd)
    except MySQLSystemdFileNotExists as err:
        raise err
    logging.info("ends start mysql .")


def stop_mysql(port: int = 3306):
    """关闭 MySQL 数据库

    Parameter:
    ----------
    port: int
        MySQL 端口号

    Returns:
    -------
    None

    Exceptions:
    -----------
    MySQLSystemdFileNotExists
    """
    # 如果 systemd 配置文件不存在就报异常
    logging.info("starts stop mysql .")
    try:
        check_mysql_systemd_exists(port)
        # 没有报异常，说明 systemd 配置存在
        # 执行 stop 操作
        stop_cmd = "systemctl stop mysqld-{}".format(port)
        logging.info("execute '{}' ".format(stop_cmd))
        exe_shell_cmd(stop_cmd)
    except MySQLSystemdFileNotExists as err:
        raise err
    logging.info("ends stop mysql .")


def create_user_and_dirs(port: int = 3306):
    """根据端口号创建 MySQL 用户

    Parameter:
    ----------
    port: int
        MySQL 的端口号

    Return:
    -------
        None
    """
    logging.info("starts create user and dirs port = {} .".format(port))

    # 创建用户
    user = MySQLUser(port)
    user.create()

    # 创建 datadir & binlogdir
    datadir = Path(dbm_agent_config.mysql_datadir_parent) / str(port)
    binlogdir = Path(dbm_agent_config.mysql_binlogdir_parent) / str(port)

    if not datadir.exists():
        logging.info("create datadir '{}' .".format(datadir))
        os.mkdir(datadir)
    else:
        logging.warning("datadir exists, skip cretae it .")

    if not binlogdir.exists():
        logging.info("create binlogdir '{}' .".format(binlogdir))
        os.mkdir(binlogdir)
    else:
        logging.warning("binlogdir exists, skip cretae it .")

    user.chown(datadir)
    user.chown(binlogdir)

    logging.info("ends create user and dirs .".format(port))


def backup_dirs(port: int = 3306, suffix=None):
    """备份数据目录和 binlog 目录，如果 suffix 为 None 就用当前时间值

    Parameters:
    -----------
    port: int
        MySQL 端口号
    
    suffix: str
        备份文件后缀
    
    Returns:
    --------
    None
    """
    # 计算 suffix
    if suffix is None:
        suffix = datetime.now().isoformat().replace(':', '-').replace('.', '-')
    
    # 计算当前的 datadir 和 binlogdir
    datadir = Path(dbm_agent_config.mysql_datadir_parent) / str(port)
    binlogdir = Path(dbm_agent_config.mysql_binlogdir_parent) / str(port)

    datadir_backup_dir = '{}-backup-{}'.format(datadir, suffix)
    binlogdir_backup_dir = '{}-backup-{}'.format(binlogdir, suffix)

    shutil.move(datadir, datadir_backup_dir)
    shutil.move(binlogdir, binlogdir_backup_dir)


def backup_config_file(port: int = 3306, suffix=None):
    """备份配置文件
    """
    # 计算 suffix
    if suffix is None:
        suffix = datetime.now().isoformat().replace(':', '-').replace('.', '-')
    datadir = Path(dbm_agent_config.mysql_datadir_parent) / str(port)
    if not datadir.exists():
        logging.warn("datadir not exists, skip copy config file to datadir .")
        return

    config_file  = "/etc/my-{}.cnf".format(port)
    config_backup_file = datadir / "my-{}.cnf-backup-{}".format(port, suffix)
    shutil.copyfile(config_file, config_backup_file)


def decompression_pkg(pkg: Path = default_pkg):
    """解压安装包到 /usr/local/

    Parameter:
    ---------
    pkg: Path
        MySQL 安装包的全路径

    Return:
    -------
        None

    Exception:
    ---------
        MySQLPkgFileNotExistsException
    """
    logging.info("starts decompression pkg .")

    if not pkg.exists():
        logging.error("mysql install package not find '{}' .".format(pkg))

        raise MySQLPkgFileNotExistsException(pkg)

    basedir = pkg_to_basedir(pkg)
    flag_file = basedir / ".dbm-agent-decompression.txt"
    if flag_file.exists():
        logging.info("ends decompression pkg .")
        return

    # 准备解压
    logging.info("open tar file {}".format(pkg))
    with tarfile.open(pkg) as tar_pkg:
        tar_pkg.extractall("/usr/local/")

    # 解压完成之后写入标记文件 basedir/.dbm-agent-decompression.txt
    with open(flag_file, 'w') as f:
        f.write('dbm-agent')

    # 解压完成
    logging.info("ends decompression pkg .")


def create_mysql_config_file(port: int = 3306, basedir: Path = None, innodb_buffer_pool_size: str = "128M"):
    """创建 MySQL 配置文件

    Parameter:
    ----------
    port: int 
        MySQL 端口号、默认值 3306

    basedir: Path
        MySQL basedir

    innodb_buffer_pool_size: int
        缓冲池的大小

    Return:
    -------
        None
    """
    logging.info(
        "starts create mysql config file. basedir = '{}', port = '{}', innodb_buffer_pool_size = '{}' .".format(basedir, port, innodb_buffer_pool_size))

    config = MySQLConfig(basedir=str(basedir), port=port,
                         innodb_buffer_pool_size=innodb_buffer_pool_size)
    config.calcu_second_attrs()
    config.generate_cnf_config_file()
    config.generate_init_cnf_config_file()
    config.generate_systemd_cnf_config()

    logging.info("ends create mysql config file.")


def init_mysql(port: int = 3306, basedir: Path = None):
    """初始化 MySQL

    Parameter:
    ----------
    port: int
        MySQL 端口号

    basedir: Path
        MySQL basedir

    Return:
    -------
        None
    """
    logging.info(
        "starts init mysql port = '{}', basedir = '{}' .".format(port, basedir))

    mysqld = Path(basedir) / "bin/mysqld"
    config = Path("/tmp/mysql-8.0-init.cnf")

    init_cmd = "{} --defaults-file={} --initialize-insecure".format(
        mysqld, config)
    logging.info("init-cmd = '{}' .".format(init_cmd))
    exe_shell_cmd(init_cmd)

    logging.info("ends init mysql.")


def install_mysql(port: int = 3306, pkg: Path = None, innodb_buffer_pool_size: str = "128M"):
    """安装 MySQL 实例

    Parameter:
    ----------
    port: int
        MySQL 端口号

    pkg: Path
        MySQL 安装包全路径

    Returns:
    --------
    None

    Exceptions:
    -----------
    MySQLPkgFileNotExistsException

    InstanceHasBeenInstalledException
    """
    # 安装前的检查
    try:
        checks_for_install(port, pkg)
    except MySQLPkgFileNotExistsException as err:
        logging.error("pkg not exists, skip install . {} .".format(err))
        raise err
    except InstanceHasBeenInstalledException as err:
        logging.error("instance has been installed {} .".format(err))
        raise err
    except Exception as err:
        logging.info("unknown Exception {}".format(err))
        raise err

    # 第一步 创建用户和目录
    create_user_and_dirs(port)

    # 第二步 解压安装包
    decompression_pkg(pkg)

    # 第三步 计算 basedir
    basedir = pkg_to_basedir(pkg)

    # 第四步 创建配置文件
    create_mysql_config_file(port=port, basedir=basedir,
                             innodb_buffer_pool_size=innodb_buffer_pool_size)

    # 第五步 初始化 mysql 实例
    init_mysql(port=port, basedir=basedir)

    # 第六步 启用 mysqld 服务
    enable_systemd_for_mysql(port)

    # 第七步 启动 mysql 实例
    start_mysql(port)

    # export PATH
    # export headers
    # export so


def uninstall_mysql(port: int = 3306):
    """卸载 mysql 数据库

    Exceptions:
    -----------

    MySQLSystemdFileNotExists
    """
    stop_mysql(port)
    disable_systemd_for_mysql(port)
    backup_config_file(port)
    backup_dirs(port)
