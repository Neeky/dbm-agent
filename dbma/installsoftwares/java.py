"""
实现 linux 系统上的 java jdk 安装。
"""

from dbma.bil import fs, sudos
from dbma.loggers.loggers import get_logger
from dbma.installsoftwares.base import BinaryInstall

logger = get_logger(__file__)

class JavaInstall(BinaryInstall):
    logger = logger.getChild("JavaInstall")

    def __init__(self, pkg="TencentKona-17.0.3.b1-jdk_linux-x86_64.tar.gz"):
        logger = self.logger.getChild("__init__")
        logger.info(f"install java using {pkg}")

        BinaryInstall.__init__(self,"root", pkg)

    def make_link(self):
        """
        创建 java 的链接文件
        """
        logger = self.logger.getChild("make_link")
        
        # 创建链接
        src = fs.join(self._install_dir, fs.get_tar_file_name(fs.join(self._pkg_repo_dir, self._pkg)))
        dest = fs.join(self._install_dir, "java")
        if fs.is_file_exists(dest):
            return

        fs.link(src, dest)
    
    def exports(self):
        # 导出环境变量
        with sudos.sudo():
            self.export_env("PATH", "/usr/local/java/bin/")
            self.export_env("JAVA_HOME", "/usr/local/java")

    def install(self):
        """
        """
        logger = self.logger.getChild("install")
        logger.info(f"going to install java ")

        # 安装 java
        BinaryInstall.install(self)

        logger.info(f"done ")

    def chown(self):
        pass

    @classmethod
    def is_version_supportted(cls, version):
        """
        根据版本号来确认是不是一个被支持的版本

        Parameters:
        ----------
        version: int | str
            jkd 版本号
        """
        if isinstance(version, int):
            version = str(version)
        
        return version in ['8', '11', '17']

    @classmethod
    def find_java_pkg(cls, version):
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
        cls_logger = cls.logger.getChild("find_java_pkg")
        # 第一步，统一转成 str
        if isinstance(version, int):
            version = str(version)
        
        # 第二步，根据 jdk_version 检查满足条件的包
        import re
        pattern = re.compile(r"^TencentKona-.*linux-x86_64.*.tar.gz$")

        pkgs = []
        import os
        for item in os.listdir(cls._pkg_repo_dir):
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

        # 第一步，确认当前给定的版本 dbm-agent 是否支持
        if not cls.is_version_supportted(jdk_version):
            message = f"{jdk_version} is not supported ."
            cls_logger.error(message)
            raise ValueError(message)
        
        # 第二步，如果支持、就去找安装包,如果 pkg 是 None 说明没有找到包
        pkg = cls.find_java_pkg(jdk_version)
        if pkg is None:
            message = "pkg not find in pkg repo dir ."
            cls_logger.error(message)
            raise ValueError(message)
        
        # 第三步，到这里说明所有的准备工作都没有问题、开始准备安装器
        return JavaInstall(pkg)
