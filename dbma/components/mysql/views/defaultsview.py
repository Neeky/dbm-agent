# -*- encoding: utf-8 -*-

"""MySQL 安装的相关接口
"""

import re
import logging
from aiohttp import web
from pathlib import Path
from dbma.bil.fun import fname
from dbma.core import messages
from dbma.bil.sudos import sudo
from dbma.core.router import routes
from dbma.core.configs import dbm_agent_config
from dbma.core.threads.backends import threads
from dbma.core.views.response import ResponseEntity
from dbma.components.mysql.commons import default_pkg
from dbma.components.mysql.install import uninstall_mysql
from dbma.components.mysql.instance import is_instance_exists
from dbma.components.mysql.views.handlers import clone_local_data_task_handler
from dbma.components.mysql.views.handlers import install_mysql_source_task_handler
from dbma.components.mysql.views.handlers import install_mysql_replica_task_handler


@routes.view("/apis/mysqls/defaults")
class MySQLDefaultsView(web.View):
    """
    MySQL 的全局默认配置
    """

    async def get(self):
        """返回 MySQL 的全局默认配置"""
        logging.info(messages.VIEW_FUN_STARTS.format(self.request.url))
        resposne = ResponseEntity(
            message="",
            error="",
            data={
                "mysql-datadir-parent": dbm_agent_config.mysql_datadir_parent,
                "mysql-default-version": dbm_agent_config.mysql_default_version,
                "mysql-binlogdir-parent": dbm_agent_config.mysql_binlogdir_parent,
            },
        )
        logging.info(messages.VIEW_FUN_ENDS.format(self.request.url))
        return web.json_response(resposne.to_dict(), status=200)


@routes.view("/apis/mysqls/install")
class MySQLInstallView(web.View):
    """
    MySQL 安装逻辑

    详细步骤:
    1. 检查 post 参数
    2. 如果参数中带了 task-id 就以任务的方式，放后台执行 & 返回结果告诉调用方，任务已经提交
    3. 如果参数中没有 task-id 就同步以同步的方式安装 MySQL & 返回结果告诉调用方，安装失败还是成功
    """

    port: int = None
    ibps: str = None
    pkg_name: str = None
    pkg: str = None
    source: str = None
    role: str = None
    task_id: str = None
    response: ResponseEntity = None

    async def parser_post_args(self):
        """处理 post 参数"""
        logging.info(messages.FUN_STARTS.format(fname()))
        data = await self.request.json()

        if "role" not in data:
            self.response.message = "instance 'role' arg miss, you can choise one of ['master', 'slave', 'source', 'replica']"
            return
        self.role = data["role"]

        if "port" not in data:
            self.response.message = messages.ARG_NOT_IN_POST_DICT.format("port")
            logging.warn(messages.FUN_ENDS.format(fname()))
            return
        self.port = int(data["port"])

        if "ibps" not in data:
            self.response.message = messages.ARG_NOT_IN_POST_DICT.format("ibps")
            logging.warn(messages.FUN_ENDS.format(fname()))
            return
        self.ibps = data["ibps"]

        # 如果没有指定 pkg-name 那么就使用默认值
        if "pkg-name" not in data:
            self.pkg_name = default_pkg.name
        self.pkg_name = data["pkg-name"]
        self.pkg = Path("/usr/local/dbm-agent/pkgs/") / self.pkg_name

        # source 可以没有，如果有那 source 一定要格式正确
        if "source" not in data:
            self.source = None
        else:
            self.source = data["source"]
            p = re.compile("\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}:\d{1,4}")
            if not p.match(self.source):
                self.response.message = "source arg format error"
                return

        # task-id 可以不传
        if "task-id" not in data:
            self.task_id = None
        else:
            self.task_id = data["task-id"]

        logging.info(messages.FUN_ENDS.format(fname()))

    async def check_args(self):
        """检查参数之间是否有逻辑冲突"""
        if self.role in ("source", "master"):
            if self.source is None:
                self.response.message = (
                    "args role = '{}', you must give 'source' arg ".format(self.role)
                )
                return

    async def install_dispatch(self):
        """根据参数决定怎么安装 MySQL"""
        # 根据 task_id 是不是 None 来决定接口是同步执行还是异步执行
        if self.task_id is not None:
            # 进入异步处理逻辑
            # ---------------
            if self.role in ("master", "source"):
                # 进入安装单机/主库的处理逻辑
                threads.submit(
                    install_mysql_source_task_handler,
                    port=self.port,
                    ibps=self.ibps,
                    pkg=self.pkg,
                    task_id=self.task_id,
                )
                self.response.message = (
                    "submit install mysql 'master|source' task to backends threads."
                )
            elif self.role in ("slave", "replica"):
                # 进入备机的处理逻辑
                source_ip, source_port = self.source.split(":")
                threads.submit(
                    install_mysql_replica_task_handler,
                    port=self.port,
                    ibps=self.ibps,
                    pkg=self.pkg,
                    source_ip=source_ip,
                    source_port=source_port,
                    task_id=self.task_id,
                )
                self.response.message = (
                    "submit install mysql 'slave|replica' task to backends threads."
                )
            logging.info(messages.VIEW_FUN_ENDS.format(self.request.url))
            # return web.json_response(self.response.to_dict(), status=200)
        else:
            # 进入同步处理逻辑
            # -------------
            if self.role in ("master", "source"):
                # 进入安装单机/主库的处理逻辑
                install_mysql_source_task_handler(
                    port=self.port, ibps=self.ibps, pkg=self.pkg, task_id=self.task_id
                )
                self.response.message = "install mysql 'master|source' complete ."
            elif self.role in ("slave", "replica"):
                # 进入备机的处理逻辑
                source_ip, source_port = self.source.split(":")
                install_mysql_replica_task_handler(
                    port=self.port,
                    ibps=self.ibps,
                    pkg=self.pkg,
                    source_ip=source_ip,
                    source_port=source_port,
                    task_id=self.task_id,
                )
                self.response.message = "install mysql 'slave|replica' complete ."

    async def post(self):
        logging.info(messages.VIEW_FUN_STARTS.format(self.request.url))
        response = ResponseEntity(message="", error="", data=None)

        await self.parser_post_args()
        await self.check_args()
        if self.response.message:
            return web.json_response(self.response.to_dict(), status=500)

        # 打印一下接收到的参数
        logging.info(
            "port = '{}', ibps = '{}', pkg-name = '{}', pkg = '{}', source = '{}', role = '{}' task-id = {} .".format(
                self.port,
                self.ibps,
                self.pkg_name,
                self.pkg,
                self.source,
                self.role,
                self.task_id,
            )
        )

        self.install_dispatch()

        logging.info(messages.VIEW_FUN_ENDS.format(self.request.url))
        return web.json_response(response.to_dict(), status=200)


@routes.view("/apis/mysqls/uninstall")
class MySQLUninstallView(web.View):
    """MySQL 卸载逻辑

    1. 检查 port 参数有没有传递
    2. 检查 port 对应的实例是否存在于当前机器上
    3. 执行删除逻辑
    """

    async def post(self):
        logging.info(messages.VIEW_FUN_STARTS.format(self.request.url))

        data = await self.request.json()
        response = ResponseEntity(message="", error="", data=None)

        # region args-check
        # 检查 port 参数
        if "port" not in data:
            response.message = "port not in post dict"
            logging.warn(response.message)
            logging.warn(messages.VIEW_FUN_ENDS.format(self.request.url))
            return web.json_response(response.to_dict(), status=500)
        port = int(data["port"])
        # endregion args-check

        # region instance-exists-check
        # 检查给定的实例是否存在
        if not is_instance_exists(port):
            response.message = "instance {} not exists.".format(port)
            response.error = response.message
            logging.warn(messages.VIEW_FUN_ENDS.format(self.request.url))
            return web.json_response(response.to_dict(), status=500)
        # endregion instance-exists-check

        # region uninstall-mysql
        try:
            with sudo("install mysql {}".format(port)):
                uninstall_mysql(port)
            response.message = "uninstall mysql complete ."
            logging.info(response.message)
        except Exception as err:
            response.message = "got error on uninstall mysql {} .".format(port)
            response.error = response.message
            logging.error(response.message)
            logging.warn(messages.VIEW_FUN_ENDS.format(self.request.url))
            return web.json_response(response.to_dict(), status=500)

        # 到这里说明正确的完成了
        logging.info(messages.VIEW_FUN_ENDS.format(self.request.url))
        return web.json_response(response.to_dict(), status=200)
        # endregion uninstall-mysql


@routes.view("/apis/mysqls/{port}/exists")
class MySQLInstanceInfoView(web.View):
    port: int = None
    response: ResponseEntity = None

    async def parser_get_args(self):
        """处理 get 参数"""
        logging.info(messages.FUN_STARTS.format(fname()))

        if self.request.match_info.get("port"):
            self.port = int(self.request.match_info.get("port"))
        else:
            self.port = None
            self.response.message = messages.ARG_NOT_IN_POST_DICT.format("port")

        logging.info(messages.FUN_ENDS.format(fname()))

    async def get(self):
        """检查给定端口的 MySQL 数据库实例是否存在"""
        logging.info(messages.VIEW_FUN_STARTS.format(self.request.url))
        # 准备返回结果对象
        self.response = ResponseEntity(
            message="", error=None, data={"exists": False, "port": None}
        )

        # 检查参数
        await self.parser_get_args()
        if self.response.message:
            return web.json_response(self.response.to_dict(), status=500)

        self.response.data["exists"] = is_instance_exists(self.port)
        self.response.data["port"] = self.port

        # 检查实例是否存在并返回结果
        logging.info(messages.VIEW_FUN_ENDS.format(self.request.url))
        return web.json_response(self.response.to_dict(), status=200)


@routes.view("/apis/mysqls/{port}/backup")
class MySQLBackupView(web.View):
    port: int = None
    backup_type: str = None
    response: ResponseEntity = None

    async def parser_get_args(self):
        """处理 get 参数"""
        logging.info(messages.FUN_STARTS.format(fname()))

        if not self.request.match_info.get("port"):
            self.response.message = messages.ARG_NOT_IN_POST_DICT.format("port")
            return
        self.port = int(self.request.match_info.get("port"))

        logging.info(messages.FUN_ENDS.format(fname()))

    async def parser_post_args(self):
        """处理 post 参数"""
        logging.info(messages.FUN_STARTS.format(fname()))
        data = await self.request.json()
        if "backup-type" not in data:
            self.response.message = messages.ARG_NOT_IN_POST_DICT.format("backup-type")
            return
        self.backup_type = data["backup-type"]
        logging.info(messages.FUN_ENDS.format(fname()))

    async def backup_dispatch(self):
        """"""
        if self.backup_type == "clone":
            threads.submit(
                clone_local_data_task_handler,
                port=self.port,
                backup_type=self.backup_type,
            )
            self.response.message = (
                "submit backup mysql using clone task to backends threads."
            )
            logging.info(messages.VIEW_FUN_ENDS.format(self.request.url))
            return web.json_response(self.response.to_dict(), status=200)

        raise ValueError("not suported backp type {}".format(self.backup_type))

    async def post(self):
        """处理备份逻辑"""
        logging.info(messages.VIEW_FUN_STARTS.format(self.request.url))

        self.response = ResponseEntity(message="", error=None, data=None)

        # region args-check
        await self.parser_get_args()
        await self.parser_post_args()
        if self.response.message:
            return web.json_response(self.response.to_dict(), status=500)
        # endregion args-check

        # 备份
        try:
            self.backup_dispatch()
        except Exception as err:
            self.response.message = str(err)
            self.response.error = err
        logging.warn(messages.VIEW_FUN_ENDS.format(self.request.url))
        return web.json_response(self.response.to_dict(), status=500)
