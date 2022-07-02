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
    def maker(cls, jdk_version=17):
        """
        根据 jdk 版本创建实例
        """
        # 第一步确认一下 jkd_version 参数的类型，如果是 int 要转成 str
        if isinstance(jdk_version, int):
            jdk_version = str(jdk_version)
        
        if jdk_version not in ["8", "11", "17"]:
            raise ValueError(f"jdk_version must be 8, 11 or 17, but got {jdk_version}")
        
        # 第二步，根据 jdk_version 检查满足条件的包
        import re
        pattern = re.compile(r"^TencentKona-.*linux-x86_64.*.tar.gz$")

        pkgs = []
        import os
        for item in os.listdir(cls._pkg_repo_dir):
            if pattern.match(item) and item.startswith(f"TencentKona-{jdk_version}"):
                pkgs.append(item)

        # 第三步，如果有包就取最高版本的
        if len(pkgs) > 0:
            pkg = pkgs[-1]
        else:
            raise ValueError(f"no jdk {jdk_version} package found")
        
        # 第四步，创建实例
        ji = JavaInstall(pkg)
        return ji
                

    
