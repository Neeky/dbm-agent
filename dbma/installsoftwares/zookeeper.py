# -*- encoding: utf-8 -*-
"""
实现 linux 系统上的 zookeeper 安装(Binary 方式安装)。
"""

from dbma.bil import fs, sudos
from dbma.loggers.loggers import get_logger
from dbma.installsoftwares.base import BinaryInstall
from dbma.bil.osuser import ZookeeperUser
from dbma.bil.cmdexecutor import exe_shell_cmd
from dbma.installsoftwares.configrenders.renders import ZookeeperConfigRender

logger = get_logger(__file__)

class ZookeeperInstall(BinaryInstall):
    """
    zookeeper 安装功能
    """
    logger = logger.getChild("ZookeeperInstall")

    target_link = "/usr/local/zookeeper"
    user = ZookeeperUser()

    def __init__(self, pkg="apache-zookeeper-3.7.1-bin.tar.gz"):
        """
        """
        BinaryInstall.__init__(self, pkg)

    def exports(self):
        self.export_env("PATH", fs.join(self.target_link, "bin"))

    def config(self, config_render=None):
        """
        """
        if config_render is None:
            config_render = ZookeeperConfigRender()
        
        with open("/usr/local/zookeeper/conf/zoo.cfg", "w") as f:
            f.write(config_render.render())
        
        if fs.is_file_exists("/data/zookeeper"):
            fs.mkdir("/data/zookeeper")
        
        self.user.chown("/data/zookeeper")

    def start(self):
        """
        """
        with sudos.sudo("start zookeeper") as _:
            exe_shell_cmd("/usr/local/zookeeper/bin/zkServer.sh")

    @classmethod
    def pkgs(cls):
        """
        只返回 java 的安装包
        """
        return [_ for _ in BinaryInstall.pkgs() if _.startswith("apache-zookeeper")]

    @classmethod
    def find_newest_pkg(cls, version):
        """
        根据 version 中给定的版本号在 /usr/local/dbm-agent/pkg/ 中找到最高的子版本

        Parameters:
        -----------
        version: int|str
            zookeeper 大版本号(3)

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
        pattern = re.compile(r"^apache-zookeeper-.*tar.gz$")

        pkgs = []
        for item in cls.pkgs():
            if pattern.match(item) and item.startswith(f"apache-zookeeper-{version}"):
                cls_logger.info(f"find pkg {item} in pkg repo dir .")
                pkgs.append(item)

        # 第三步，如果有包就取最高版本的安装包
        return pkgs[-1] if len(pkgs) > 0 else None

    @classmethod
    def maker(cls, zookeeper_version=3):
        """
        根据 jdk 版本创建实例
        """
        cls_logger = cls.logger.getChild("maker")
        
        # 第一步，如果支持、就去找安装包,如果 pkg 是 None 说明没有找到包
        pkg = cls.find_newest_pkg(zookeeper_version)
        if pkg is None:
            message = "pkg not find in pkg repo dir ."
            cls_logger.error(message)
            raise ValueError(message)
        
        # 第三步，到这里说明所有的准备工作都没有问题、开始准备安装器
        return ZookeeperInstall(pkg)
