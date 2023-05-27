# -*- coding: utf-8 -*-

"""
Redis 相关的公共函数
"""

import re
from pathlib import Path

from dbma.bil.fs import is_file_exists
from dbma.core.configs import dbm_agent_config

# Redis 的默认端口号
default_redis_port = 6379

# 根据 dbm-agent 的配置文件确认默认情况下使用的 Redis 版本号
default_redis_pkg = Path(
    "/usr/local/dbm-agent/pkgs/redis-7.0.11-linux-glibc-2.34-x86_64.tar.gz"
)

# Redis 安装包的正则表达式
redis_pkg_re_pattern = re.compile(
    r"redis-(?P<redis_version>\d{1,2}.\d{1,2}.\d{1,3})-linux-glibc-(?P<glibc_version>\d.\d{1,2})-x86_64.tar.gz"
)


def port_to_redis_systemd_config_file(port: int = 6378):
    """根据 Port 生成 Redis Systemd 配置文件全路径

    Parameters
    ----------
    port : int, optional
        Redis 的端口号, by default 6378
    """
    return Path("/usr/lib/systemd/system/redisd-{}.service".format(port))


def is_redis_systemd_config_file_exists(port: int = 6378):
    """Redis 的 Systemd 配置文件是否存在

    Parameters
    ----------
    port : int, optional
        Redis 的端口号, by default 6378
    """
    systemd_config_file = port_to_redis_systemd_config_file(port)
    try:
        return is_file_exists(systemd_config_file)
    except TypeError as err:
        return False
    except ValueError as err:
        return False
    except Exception as err:
        return False


def disable_redis_systemd(port: int = 6378):
    """禁用对应实例的 Redis systemd 配置

    Parameters
    ----------
    port : int, optional
        实例的端口号, by default 6378
    """
    pass
