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
from dbma.bil.fun import fname
from dbma.core import messages
from dbma.bil.osuser import MySQLUser
from dbma.bil.cmdexecutor import exe_shell_cmd
from dbma.core.configs import dbm_agent_config
from dbma.components.mysql.config import MySQLConfig
from dbma.components.mysql.commons import get_mysql_version
from dbma.components.mysql.commons import export_cmds_to_path
from dbma.components.mysql.commons import pkg_to_basedir, default_pkg
from dbma.components.mysql.commons import export_header_files, export_so_files
from dbma.components.mysql.exceptions import MySQLSystemdFileNotExists
from dbma.components.mysql.exceptions import MySQLPkgFileNotExistsException
from dbma.components.mysql.exceptions import InstanceHasBeenInstalledException


def create_init_sql_file(version: str = None):
    """生成 init-sql 文件给 init 的时候用

    Parameters:
    -----------

    version: str
        MySQL 版本号

    Exception:
    ----------
    ValueError
    """
    logging.info(messages.FUN_STARTS.format(fname()))

    import dbma

    if version is None:
        message = "mysql version is None, can't create init-sql-file ."
        logging.error(message)
        raise ValueError(messages)

    # 检查版本号并根据版本号生成配置文件
    if version.startswith("8.0"):
        sql_file = Path(dbma.__file__).parent / "static/cnfs/init-8.0.x.sql"
    elif version.startswith("5.7"):
        sql_file = Path(dbma.__file__).parent / "static/cnfs/init-5.7.x.sql"
    else:
        message = "mysql version is '{}', can't create init-sql-file .".format(version)
        logging.error(message)
        raise ValueError(messages)
    logging.info("init sql file = {}".format(sql_file))

    # 复制文件
    shutil.copy(sql_file, dbm_agent_config.mysql_init_user_sql_file)
    logging.info(messages.FUN_ENDS.format(fname()))


def remove_init_sql_file():
    """清理 /tmp/mysql-init.sql 文件"""
    logging.info(messages.FUN_STARTS.format(fname()))

    init_sql_file = Path(dbm_agent_config.mysql_init_user_sql_file)
    if init_sql_file.exists():
        os.remove(init_sql_file)

    logging.info(messages.FUN_ENDS.format(fname()))


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
    logging.info(messages.FUN_STARTS.format(fname()))
    if not pkg.exists():
        logging.warn(messages.FILE_NOT_EXISTS.format(pkg))
        raise MySQLPkgFileNotExistsException(messages.FILE_NOT_EXISTS.format(pkg))

    # 检查给定的实例是不是已经安装过了
    datadir = Path(dbm_agent_config.mysql_datadir_parent) / "{}".format(port)
    if datadir.exists():
        logging.warn(messages.MYSQL_INSTANCE_HAS_EXISTS.format(port))
        raise InstanceHasBeenInstalledException(str(port))

    logging.info(messages.FUN_ENDS.format(fname()))


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
    logging.info(messages.FUN_STARTS.format(fname()))

    systemd_file = Path("/usr/lib/systemd/system/") / "mysqld-{}.service".format(port)
    if not systemd_file.exists():
        logging.error(messages.FILE_NOT_EXISTS.format(systemd_file))
        raise MySQLSystemdFileNotExists(systemd_file)

    logging.info(messages.FUN_ENDS.format(fname()))


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
    logging.info(messages.FUN_STARTS.format(fname()))

    try:
        check_mysql_systemd_exists(port)
        # 没有报异常，说明 systemd 配置存在, 准备执行 enable 操作
        enable_cmd = "systemctl enable mysqld-{}".format(port)
        logging.info(messages.EXECUTE_CMD.format(enable_cmd))
        exe_shell_cmd(enable_cmd)
    except MySQLSystemdFileNotExists as err:
        raise err

    logging.info(messages.FUN_ENDS.format(fname()))


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
    logging.info(messages.FUN_STARTS.format(fname()))

    try:
        check_mysql_systemd_exists(port)
        # 没有报异常，说明 systemd 配置存在
        # 执行 enable 操作
        disable_cmd = "systemctl disable mysqld-{}".format(port)
        logging.info(messages.EXECUTE_CMD.format(disable_cmd))
        exe_shell_cmd(disable_cmd)
    except MySQLSystemdFileNotExists as err:
        logging.info(err)
        raise err

    logging.info(messages.FUN_ENDS.format(fname()))


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
    logging.info(messages.FUN_STARTS.format(fname()))

    try:
        check_mysql_systemd_exists(port)
        # 没有报异常，说明 systemd 配置存在
        # 执行 start 操作
        start_cmd = "systemctl start mysqld-{}".format(port)
        logging.info(messages.EXECUTE_CMD.format(start_cmd))
        exe_shell_cmd(start_cmd)
    except MySQLSystemdFileNotExists as err:
        raise err

    logging.info(messages.FUN_ENDS.format(fname()))


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
    logging.info(messages.FUN_STARTS.format(fname()))

    try:
        check_mysql_systemd_exists(port)
        # 没有报异常，说明 systemd 配置存在
        # 执行 stop 操作
        stop_cmd = "systemctl stop mysqld-{}".format(port)
        logging.info(messages.EXECUTE_CMD.format(stop_cmd))
        exe_shell_cmd(stop_cmd)
    except MySQLSystemdFileNotExists as err:
        raise err

    logging.info(messages.FUN_ENDS.format(fname()))


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
    logging.info(messages.FUN_STARTS.format(fname()))

    # 创建用户
    user = MySQLUser(port)
    user.create()

    # 创建 datadir & binlogdir
    datadir = Path(dbm_agent_config.mysql_datadir_parent) / str(port)
    binlogdir = Path(dbm_agent_config.mysql_binlogdir_parent) / str(port)

    if not datadir.exists():
        logging.info(messages.CREATE_DIR.format(datadir))
        os.mkdir(datadir)
    else:
        logging.warning(messages.DIR_EXISTS.format(datadir))

    if not binlogdir.exists():
        logging.info(messages.CREATE_DIR.format(binlogdir))
        os.mkdir(binlogdir)
    else:
        logging.warning(messages.DIR_EXISTS.format(binlogdir))

    user.chown(datadir)
    user.chown(binlogdir)

    logging.info(messages.FUN_ENDS.format(fname()))


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
    logging.info(messages.FUN_STARTS.format(fname()))

    # 计算 suffix
    if suffix is None:
        suffix = datetime.now().isoformat().replace(":", "-").replace(".", "-")

    # 计算当前的 datadir 和 binlogdir
    datadir = Path(dbm_agent_config.mysql_datadir_parent) / str(port)
    binlogdir = Path(dbm_agent_config.mysql_binlogdir_parent) / str(port)

    datadir_backup_dir = "{}-backup-{}".format(datadir, suffix)
    binlogdir_backup_dir = "{}-backup-{}".format(binlogdir, suffix)

    shutil.move(datadir, datadir_backup_dir)
    shutil.move(binlogdir, binlogdir_backup_dir)

    logging.info(messages.FUN_ENDS.format(fname()))


def backup_config_file(port: int = 3306, suffix=None):
    """备份配置文件

    Parameters:
    -----------
    port: int
        MySQL 端口号

    suffix: str
        备份文件的后缀

    Return:
    -------

    """
    logging.info(messages.FUN_STARTS.format(fname()))

    # 计算 suffix
    if suffix is None:
        suffix = datetime.now().isoformat().replace(":", "-").replace(".", "-")
    datadir = Path(dbm_agent_config.mysql_datadir_parent) / str(port)
    if not datadir.exists():
        logging.warn(messages.DIR_NOT_EXISTS.format(datadir))
        return

    config_file = "/etc/my-{}.cnf".format(port)
    config_backup_file = datadir / "my-{}.cnf-backup-{}".format(port, suffix)
    logging.info(messages.MOVE_FILE_TO.format(config_file, config_backup_file))

    # 备份文件
    shutil.copyfile(config_file, config_backup_file)

    logging.info(messages.FUN_ENDS.format(fname()))


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
    logging.info(messages.FUN_STARTS.format(fname()))

    if not pkg.exists():
        logging.error(messages.FILE_NOT_EXISTS.format(pkg))
        raise MySQLPkgFileNotExistsException(messages.FILE_NOT_EXISTS.format(pkg))

    basedir = pkg_to_basedir(pkg)
    flag_file = basedir / ".dbm-agent-decompression.txt"
    if flag_file.exists():
        logging.info("ends decompression pkg .")
        return

    # 准备解压
    with tarfile.open(pkg) as tar_pkg:
        tar_pkg.extractall("/usr/local/")

    # 解压完成之后写入标记文件 basedir/.dbm-agent-decompression.txt
    with open(flag_file, "w") as f:
        f.write("dbm-agent")

    # 解压完成
    logging.info(messages.FUN_ENDS.format(fname()))


def create_mysql_config_file(
    port: int = 3306, basedir: Path = None, innodb_buffer_pool_size: str = "128M"
):
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
    logging.info(messages.FUN_STARTS.format(fname()))
    logging.info(
        "basedir = '{}', port = '{}', innodb_buffer_pool_size = '{}' .".format(
            basedir, port, innodb_buffer_pool_size
        )
    )

    config = MySQLConfig(
        basedir=str(basedir), port=port, innodb_buffer_pool_size=innodb_buffer_pool_size
    )

    config.calcu_second_attrs()
    config.generate_cnf_config_file()
    config.generate_init_cnf_config_file()
    config.generate_systemd_cnf_config()

    logging.info(messages.FUN_ENDS.format(fname()))


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
    logging.info(messages.FUN_STARTS.format(fname()))
    logging.info("port = '{}', basedir = '{}' .".format(port, basedir))

    mysqld = Path(basedir) / "bin/mysqld"
    config = Path(dbm_agent_config.mysql_init_cnf)

    init_cmd = "{} --defaults-file={} --init-file={} --initialize-insecure".format(
        mysqld, config, dbm_agent_config.mysql_init_user_sql_file
    )
    logging.info("init-cmd = '{}' .".format(init_cmd))
    # 执行 init 操作
    exe_shell_cmd(init_cmd)

    logging.info(messages.FUN_ENDS.format(fname()))


def install_mysql(
    port: int = 3306, pkg: Path = None, innodb_buffer_pool_size: str = "128M"
):
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
    logging.info(messages.FUN_STARTS.format(fname()))

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

    version = get_mysql_version(pkg.name)
    basedir = pkg_to_basedir(pkg)

    # 第一步 创建用户和目录
    create_user_and_dirs(port)

    # 第二步 解压安装包
    decompression_pkg(pkg)

    # 第三步 计算 basedir
    basedir = pkg_to_basedir(pkg)

    # TODO 清理掉 read_only 参数
    # 第四步 创建配置文件
    create_mysql_config_file(
        port=port, basedir=basedir, innodb_buffer_pool_size=innodb_buffer_pool_size
    )

    # 第五步 复制 init 文件
    create_init_sql_file(version)

    # 第五步 初始化 mysql 实例
    init_mysql(port=port, basedir=basedir)

    # 第六步 启用 mysqld 服务
    enable_systemd_for_mysql(port)

    # 第七步 启动 mysql 实例
    start_mysql(port)

    # 第八步 导出 PATH 环境变量
    export_cmds_to_path(basedir)

    # 第九步 导出头文件
    export_header_files(pkg)

    # 第十步 导出 so 文件
    export_so_files(pkg)

    # 清理 init-sql
    remove_init_sql_file()

    logging.info(messages.FUN_ENDS.format(fname()))


def uninstall_mysql(port: int = 3306):
    """卸载 mysql 数据库

    Exceptions:
    -----------

    MySQLSystemdFileNotExists
    """
    logging.info(messages.FUN_STARTS.format(fname()))

    # 第一步 停止 MySQL 服务
    stop_mysql(port)

    # 第二步 禁用 systemd 服务
    disable_systemd_for_mysql(port)

    # 第三步 备份配置文件
    backup_config_file(port)

    # 第四步 备份数据目录与binlog目录
    backup_dirs(port)
    logging.info(messages.FUN_ENDS.format(fname()))
