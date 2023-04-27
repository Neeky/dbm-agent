# -*- encoding: utf-8 -*-

"""Resdis 自动化配置"""

import logging
from pathlib import Path
from jinja2 import Template
from dataclasses import dataclass, asdict

from dbma.bil.fun import fname
from dbma.core import messages
from dbma.components.redis.exceptions import RedisConfigTemplateFileNotExistsException


@dataclass
class RedisConfig(object):
    """实现对 Redis 的配置文件生成

    Parameters
    ----------
    port : int
        Redis 要监控的端口
    """

    port: int = 6378
    dbfilename: str = "dump.rdb"
    loglevel: str = "notice"
    daemonize: str = "yes"
    bind: str = "127.0.0.1 ::1"
    dir: int = ""
    protected_mode: str = "yes"
    tcp_backlog: int = 511
    unixsocketperm: str = "700"
    tcp_keepalive: int = 300

    def __post__init__(self):
        """根据 port 的值来调整其它值"""
        self.dir = "/database/redis/{}".format(self.port)

    def render_config(self) -> str:
        """渲染配置文件

        Returns
        -------
        str
        """
        logging.info(messages.FUN_STARTS.format(fname()))
        import dbma

        # 模板文件的位置
        redis_config__template_file = (
            Path(dbma.__file__).parent / "static/cnfs/redis.conf.jinja"
        )

        # 配置文件模板不存在就要报异常
        if not redis_config__template_file.exists():
            msg = "redis config template file '{}' not exists Excepiton ".format(
                str(redis_config__template_file)
            )
            logging.error(msg)
            raise RedisConfigTemplateFileNotExistsException(msg)

        # 执行到这里说明配置文件模板一定是存在的，准备渲染
        content = ""
        with open(redis_config__template_file) as file_object:
            content = file_object.read()

        # 渲染配置文件，并返回渲染之后的文本
        template = Template(content)
        logging.info(messages.FUN_ENDS.format(fname()))
        return template.render(asdict(self))
