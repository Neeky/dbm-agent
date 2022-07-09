# -*- encoding: utf-8 -*-
"""
实现 linux 系统上的 java jdk 安装(Binary 方式安装).
"""

from dbma.bil import fs
from dbma.loggers.loggers import get_logger
from dbma.installsoftwares.base import BinaryInstall

logger = get_logger(__file__)


class JavaInstall(BinaryInstall):
    """
    实现 java-jdk 的安装
    """
    logger = logger.getChild("JavaInstall")

    target_link = "/usr/local/java"

    def __init__(self, pkg="TencentKona-17.0.3.b1-jdk_linux-x86_64.tar.gz"):
        BinaryInstall.__init__(self, pkg)

    @classmethod
    def pkgs(cls):
        """
        只返回 java 的安装包
        """
        return [_ for _ in BinaryInstall.pkgs() if _.startswith("TencentKona")]

    @classmethod
    def find_newest_pkg(cls, version):
        """
        根据 version 中给定的版本号在 /usr/local/dbm-agent/pkg/ 中找到最高的子版本

        Parameters:
        -----------
        version: int|str
            jdk 大版本号(8, 11, 17)

        Return:
        -------
            str
        """
        cls_logger = cls.logger.getChild("find_newest_pkg")
        # 第一步，统一转成 str
        if isinstance(version, int):
            version = str(version)
        
        # 第二步，根据 jdk_version 检查满足条件的包
        import re
        pattern = re.compile(r"^TencentKona-.*linux-x86_64.*.tar.gz$")

        pkgs = []
        for item in cls.pkgs():
            if pattern.match(item) and item.startswith(f"TencentKona-{version}"):
                cls_logger.info(f"find pkg {item} in pkg repo dir .")
                pkgs.append(item)

        # 第三步，如果有包就取最高版本的安装包
        return pkgs[-1] if len(pkgs) > 0 else None

    @classmethod
    def maker(cls, jdk_version=17):
        """
        根据 jdk 版本创建实例
        """
        cls_logger = cls.logger.getChild("maker")
        
        # 第一步，如果支持、就去找安装包,如果 pkg 是 None 说明没有找到包
        pkg = cls.find_newest_pkg(jdk_version)
        if pkg is None:
            message = "pkg not find in pkg repo dir ."
            cls_logger.error(message)
            raise ValueError(message)
        
        # 第三步，到这里说明所有的准备工作都没有问题、开始准备安装器
        return JavaInstall(pkg)

    def exports(self):
        self.export_env("PATH", fs.join(self.target_link, "bin/"))
        self.export_env("JAVA_HOME", self.target_link)

    def make_link(self):
        fs.link(self.get_src_dir_name(), self.target_link)

