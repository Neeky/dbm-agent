# -*- encoding: utf-8 -*-

"""MySQL 安装的相关接口
"""

import logging
from aiohttp import web
from pathlib import Path
from dbma.bil.sudos import sudo
from dbma.core.router import routes
from dbma.core.configs import dbm_agent_config
from dbma.components.mysql.install import install_mysql, uninstall_mysql


@routes.view("/apis/mysqls/defaults")
class MySQLDefaultsView(web.View):
    """
    MySQL 的全局默认配置
    """
    async def get(self):
        """返回 MySQL 的全局默认配置
        """
        return web.json_response({"mysql_datadir_parent": dbm_agent_config.mysql_datadir_parent,
                                  "default-version": dbm_agent_config.mysql_default_version,
                                  "mysql_binlogdir_parent": dbm_agent_config.mysql_binlogdir_parent})


@routes.view("/apis/mysqls/install")
class MySQLInstallView(web.View):
    """
    MySQL 安装逻辑
    """
    async def post(self):
        logging.info("post-request {}".format(self.request.url))

        data = await self.request.json()

        # 检查参数
        if 'port' not in data:
            logging.warn("port not in post dict")
            return web.json_response({
                'message': "port not in post dict",
            }, status=500)
        port = data['port']

        # 检查 innodb-buffer-pool-size
        if 'ibps' not in data:
            logging.warn("ibps not in post dict")
            return web.json_response({
                'message': "ibps not in post dict",
            }, status=500)
        ibps = data['ibps']

        # 检查包名
        if 'pkg-name' not in data:
            logging.warn("pkg-name not in post dict")
            return web.json_response({
                'message': "pkg-name not in post dict",
            }, status=500)
        pkg_name = data['pkg-name']
        pkg = Path("/usr/local/dbm-agent/pkgs/") / pkg_name

        # 打印一下接收到的参数
        logging.info(
            "port = '{}', ibps = '{}', pkg-name = '{}', pkg = '{}' .".format(port, ibps, pkg_name, pkg))
        try:
            # 临时把权限提升到 root (创建目录、用户 ... 都会用到)
            with sudo("install mysql {}".format(port)):
                install_mysql(port, pkg, innodb_buffer_pool_size=ibps)
            logging.info("install mysql compelete. ")

        except Exception as err:
            logging.info("install mysql got exception {}".format(err))
            return web.json_response({
                "message": str(err),
            }, status=500)
        # 执行到这里说明已经安装完成了
        return web.json_response({
            "message": 'install mysql compelet.',
        }, status=200)


@routes.view("/apis/mysqls/uninstall")
class MySQLInstallView(web.View):
    """
    MySQL 卸载逻辑
    """
    async def post(self):
        """
        """
        logging.info("post-request {}".format(self.request.url))

        data = await self.request.json()

        # 检查是不是少传了 port 参数
        if 'port' not in data:
            logging.warn("port not in post dict")
            return web.json_response({
                'message': "port not in post dict",
            }, status=500)
        
        port = data['port']
        try:
            with sudo("install mysql {}".format(port)):
                uninstall_mysql(port)
            logging.info("uninstall mysql complete .")
        except Exception as err:
            logging.error("got error on uninstall mysql {} .".format(port))
            return web.json_response({
                'message': str(err)
            }, status=500)

        # 到这里说明正确的完成了
        return web.json_response({
            'message': "uninstall mysql complete ."
        }, status=200)
        
