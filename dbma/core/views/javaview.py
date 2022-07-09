# -*- encoding: utf-8 -*-

"""实现调用接口安装 java-jdk 环境

"""

from aiohttp import web
from dbma.core.router import routes
from dbma.loggers.loggers import get_logger
from dbma.bil import fs
from dbma.installsoftwares.java import JavaInstall

logger = get_logger(__file__)


@routes.view("/java")
class JavaView(web.View):
    """
    调用接口用于检查是 java 否安装成功
    """
    logger = logger.getChild("JavaDetectView")

    async def get(self):
        """
        检查 java 是否安装成功
        """
        logger = self.logger.getChild("status")
        if JavaInstall.is_installed():
            return web.json_response({"status": "installed", "version": JavaInstall.current_installed_version()})
        return web.json_response({"status": "not installed", "version": None})

@routes.view("/java/install/{version}")
class JavaInstallView(web.View):
    """
    安装给定版本的 java 环境
    """
    logger = logger.getChild("JavaView")

    async def get(self):
        """
        安装 java
        """
        logger = self.logger.getChild("get")
        logger.info("start")
        version = self.request.match_info.get("version")
        logger.warning(f"version: {version} {type(version)}")
        if not JavaInstall.is_installed():
            ji = JavaInstall.maker(version)
            ji.install()
            return web.json_response({"status": "installed", "version": ji.current_installed_version()})
        
        return web.json_response({"status": "installed", "version": JavaInstall.current_installed_version()})
        

