# -*- coding: utf-8 -*-

"""Resdis systemd 相关的配置"""

import logging
from pathlib import Path
from jinja2 import Template
from datetime import datetime
from dataclasses import dataclass, asdict

from dbma.bil.cmdexecutor import exe_shell_cmd
from dbma.bil.fun import fname
from dbma.core import messages
from dbma.components.redis.exceptions import RedisConfigTemplateFileNotExistsException


@dataclass
class RedisSystemdConfig(object):
    port: int = 6379
    basedir: str = ""
    now: str = datetime.now().isoformat()

    def render_config(self):
        """沉浸 Redis 的 Systemd 配置文件

        Exceptions:
        -----------
        RedisConfigTemplateFileNotExistsException
        """
        logging.info(messages.FUN_STARTS.format(fname()))
        import dbma

        redis_systemd_config_template = (
            Path(dbma.__file__).parent / "static/cnfs/redisd.service.jinja"
        )
        # 检查模板文件是否存在
        if not redis_systemd_config_template.exists():
            msg = "redis systemd config file '' not exists .".format(
                redis_systemd_config_template
            )
            logging.error(msg)
            logging.error(messages.FUN_ENDS.format(fname()))
            raise RedisConfigTemplateFileNotExistsException(msg)

        # 取出配置文件并渲染
        content = ""
        with open(redis_systemd_config_template) as template_object:
            content = template_object.read()

        template = Template(content)
        logging.info(messages.FUN_ENDS.format(fname()))
        # 把 Path 转为 str
        if isinstance(self.basedir, Path):
            self.basedir = str(self.basedir)
        return template.render(asdict(self))

    def generate_systemd_config(self):
        """生成 systemd 配置文件"""
        logging.info(messages.FUN_STARTS.format(fname()))
        systemd_config_file = Path(
            "/usr/lib/systemd/system/"
        ) / "redisd-{}.service".format(self.port)
        # 保存到文件
        with open(systemd_config_file, "w") as systemd_object:
            systemd_object.write(self.render_config())
        # 生效
        cmd = "systemctl daemon-reload"
        logging.info(cmd)
        exe_shell_cmd(cmd)
        logging.info(messages.FUN_ENDS.format(fname()))
