# -*- coding: utf-8 -*-

"""安装 orchestrator
"""

import re
import tarfile
import logging
from pathlib import Path
from dbma.bil.fun import fname
from dbma.core import messages
from dbma.components.orchestrator.exceptions import (
    OrchHasBeenInstalledException,
    OrchPkgNotExistsException,
)


def assert_orch_not_installed():
    """断言 orchestrator 有没有安装，如果配置文件
    /usr/local/orchestrator/orchestrator.conf.json 存在说明安装过了

    Returns:
    --------
    None

    Exceptions:
    -----------
    OrchHasBeenInstalledException
    """
    logging.info(messages.FUN_STARTS.format(fname()))

    orch_config_file = Path("/usr/local/orchestrator/orchestrator.conf.json")
    if orch_config_file.exists():
        logging.warn(messages.FUN_ENDS.format(fname()))
        raise OrchHasBeenInstalledException("orchestrator has been installed .")

    logging.info(messages.FUN_ENDS.format(fname()))


def get_orch_version(pkg: Path):
    """根据 orch 安装包的全路径返回 orch 的版本号

    Parameters:
    -----------
    pkg: Path

    Returns:
    --------
    str
    """
    logging.info(messages.FUN_STARTS.format(fname()))

    if pkg is None:
        raise ValueError("pkg arg is None on call {} function .".format(fname()))

    pkg_name = pkg.name
    p = re.compile(r"orchestrator-(?P<version>\d{1,2}.\d{1,2}.\d{1,2})-.*\.tar.gz")

    logging.info(messages.FUN_ENDS.format(fname()))
    return p.match(pkg_name).group("version")


def decompression_pkg(pkg: Path):
    """解压 orchestrator 的安装包

    Parameters:
    -----------
    pkg:Path
        安装的的全路径

    Exceptions:
    -----------
    ValueError
    OrchPkgNotExistsException
    -----------
    """
    logging.info(messages.FUN_STARTS.format(fname()))
    if pkg is None:
        raise ValueError("pkg arg is None on call decompression_pkg function .")

    # 到这里说明 pkg 至少不为 None
    if not pkg.exists():
        raise OrchPkgNotExistsException(messages.FILE_NOT_EXISTS.format(str(pkg)))

    # flag_file 用于确认有没有解压过
    flag_file = Path("/usr/local/orchestrator-3.2.6/.dbm-agent-decompression.txt")

    # 真正的执行解压操作
    with tarfile.open(pkg) as tar_pkg:
        tar_pkg.extractall("/usr/local/")

    # 解压完成之后写入标记文件 basedir/.dbm-agent-decompression.txt
    with open("", "w") as f:
        f.write("dbm-agent")

    # 解压完成
    logging.info(messages.FUN_ENDS.format(fname()))


def install_orch(pkg: Path):
    """安装 orchestrator 到 /usr/local/

    Parameters:
    -----------
    pkg: Path
        安装包的全路径
    """
    # 断定 orch 没有安装过
    try:
        assert_orch_not_installed()
    except OrchHasBeenInstalledException as err:
        raise err

    # 解压
    # 渲染配置文件
    # 渲染 systemd 文件
    # 启动
