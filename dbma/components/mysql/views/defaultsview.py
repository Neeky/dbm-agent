# -*- encoding: utf-8 -*-

"""MySQL 安装的相关接口
"""

import logging
from aiohttp import web
from pathlib import Path
from dbma.bil.sudos import sudo
from dbma.core.router import routes
from dbma.core.configs import dbm_agent_config
from dbma.core.threads.backends import threads
from dbma.core.views.response import ResponseEntity
from dbma.components.mysql.instance import is_instance_exists
from dbma.components.mysql.install import install_mysql, uninstall_mysql
from dbma.components.mysql.views.handlers import install_mysql_task_handler


@routes.view("/apis/mysqls/defaults")
class MySQLDefaultsView(web.View):
    """
    MySQL 的全局默认配置
    """
    async def get(self):
        """返回 MySQL 的全局默认配置
        """
        logging.info("view-request-starts: {}".format(self.request.url))
        resposne = ResponseEntity(message="", error="",
                                  data={"mysql-datadir-parent": dbm_agent_config.mysql_datadir_parent,
                                        "mysql-default-version": dbm_agent_config.mysql_default_version,
                                        "mysql-binlogdir-parent": dbm_agent_config.mysql_binlogdir_parent})
        logging.info("view-requests-ends: {}".format(self.request.url))
        return web.json_response(resposne.to_dict())


@routes.view("/apis/mysqls/install")
class MySQLInstallView(web.View):
    """
    MySQL 安装逻辑
    
    详细步骤:
    1. 检查 post 参数
    2. 如果参数中带了 task-id 就以任务的方式，放后台执行 & 返回结果告诉调用方，任务已经提交
    3. 如果参数中没有 task-id 就同步以同步的方式安装 MySQL & 返回结果告诉调用方，安装失败还是成功
    """
    async def post(self):
        logging.info("view-request-starts: {}".format(self.request.url))

        data = await self.request.json()
        response = ResponseEntity(message="", error="", data=None)

        # region args-check
        # 检查 port
        if 'port' not in data:
            response.message = "port not in post dict"
            logging.warn(response.message)
            return web.json_response(response.to_dict(), status=500)
        port = data['port']

        # 检查 innodb-buffer-pool-size
        if 'ibps' not in data:
            response.message = "ibps not in post dict"
            logging.warn(response.message)
            return web.json_response(response.to_dict(), status=500)
        ibps = data['ibps']

        # 检查 pkg-name
        if 'pkg-name' not in data:
            response.message = "pkg-name not in post dict"
            logging.warn(response.message)
            return web.json_response(response.to_dict(), status=500)
        pkg_name = data['pkg-name']
        pkg = Path("/usr/local/dbm-agent/pkgs/") / pkg_name
        
        # 检查 task-id ? 参数
        if 'task-id' not in data:
            task_id = None
        else:
            task_id = data['task-id']
        # endregion args-check

        # 打印一下接收到的参数
        logging.info(
            "port = '{}', ibps = '{}', pkg-name = '{}', pkg = '{}' task-id = {}.".format(port, ibps, pkg_name, pkg, task_id))

        # region post-task-to-backends
        # 检查是不是 dbm-center 发过来的请求(如果是它会带上 task_id)
        if not task_id is None:
            threads.submit(install_mysql_task_handler, port=port,
                           ibps=ibps, pkg=pkg, task_id=task_id)
            response.message = "submit install mysql task to backends threads."
            logging.info(response.message)
            
            # 任务放后台
            logging.info("view-requests-ends: {}".format(self.request.url))
            return web.json_response(response.to_dict(), status=200)
        # endregion post-task-to-backends

        # region sync-install-mysql
        try:
            # 临时把权限提升到 root (创建目录、用户 ... 都会用到)
            with sudo("install mysql {}".format(port)):
                install_mysql(port, pkg, innodb_buffer_pool_size=ibps)
            logging.info("install mysql compelete. ")

        except Exception as err:
            response.message = "install mysql got exception {}".format(err)
            response.error = str(err)
            logging.info(response.message)
            return web.json_response(response.to_dict(), status=500)
        
        # 执行到这里说明已经安装完成了
        logging.info("view-requests-ends: {}".format(self.request.url))
        response.message = "install mysql compelet."
        return web.json_response(response.to_dict(), status=200)
        # endregion sync-install-mysql


@routes.view("/apis/mysqls/uninstall")
class MySQLUninstallView(web.View):
    """MySQL 卸载逻辑
    
    1. 检查 port 参数有没有传递
    2. 检查 port 对应的实例是否存在于当前机器上
    3. 执行删除逻辑
    """
    async def post(self):
        logging.info("view-request-starts: {}".format(self.request.url))

        data = await self.request.json()
        response = ResponseEntity(message="", error="", data=None)

        # region args-check
        # 检查 port 参数
        if 'port' not in data:
            response.message = "port not in post dict"
            logging.warn(response.message)
            return web.json_response(response.to_dict(), status=500)
        port = int(data['port'])
        # endregion args-check
        
        # region instance-exists-check
        # 检查给定的实例是否存在
        if not is_instance_exists(port):
            response.message = "instance {} not exists.".format(port)
            response.error = response.message
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
            return web.json_response(response.to_dict(), status=500)

        # 到这里说明正确的完成了
        logging.info("view-requests-ends: {}".format(self.request.url))
        return web.json_response(response.to_dict(), status=200)
        # endregion uninstall-mysql


@routes.view("/apis/mysqls/{port}/exists")
class MySQLInstanceInfoView(web.View):
    async def get(self):
        """检查给定端口的 MySQL 数据库实例是否存在
        """
        logging.info("view-request-starts: {}".format(self.request.url))
        # 准备返回结果对象
        resposne = ResponseEntity(message="", error=None, data={
            "exists": False,
            "port": None
        })
        
        # 检查参数
        if self.request.match_info.get('port'):
            port = int(self.request.match_info.get('port'))
            resposne.data['exists'] = is_instance_exists(port)
            resposne.data['port'] = port
        else:
            # 缺少参数 port 的时候直接返回
            resposne.message = "dict miss port argument."
            resposne.error = resposne.message
        
        # 检查实例是否存在并返回结果
        logging.info("view-requests-ends: {}".format(self.request.url))
        return web.json_response(resposne.to_dict())