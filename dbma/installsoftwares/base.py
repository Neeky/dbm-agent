"""
实现 linux 系统上的软件包自动化安装与卸载。
"""

from dbma.bil import fs
from dbma.bil import sudos
from dbma.loggers.loggers import get_logger
from dbma.bil.osuser import RootUser, RootGroup, MySQLGroup, MySQLUser
logger = get_logger(__file__)



class BaseInstall(object):
    """
    所有装包类的基类
    """
    logger = logger.getChild("BaseInstall")

    def user_and_group_factory(self, name_or_port):
        """
        根据用户名、获取 User 对象和 Group 对象

        Parameters:
        -----------
        name_or_port: str
            用户名或者 MySQL 端口号
        """
        logger = self.logger.getChild("user_and_group_factory")
        logger.info(f"get name '{name_or_port}' ")
        if name_or_port == "root":
            return (RootUser(), RootGroup())
        elif isinstance(name_or_port, int):
            return (MySQLUser(name_or_port), MySQLGroup("mysql"))

    def export_env(self, name, value):
        """
        配置环境变量
        Parameters:
        ----------
        bin_path: str
            PATH 环境变量值要新加的前缀

        Returns:
            None
        """
        logger = self.logger.getChild("export_env_variable")
        # 如果是 PATH 就是追加，其它的情况都是一个 name 一个值
        if name == "PATH":
            line = f"export {name}={value}:${name}"
        else:
            line = f"export {name}={value}"

        # 检查有没有配置，如果没有就添加
        if fs.is_line_in_etc_profile(line) == False:
            fs.append_new_line_to_etc_profile(line)
    
    def exports(self):
        pass

    def chown(self):
        pass

    def make_link(self):
        pass
    
    def install(self):
        """
        实现软件包的自动安装
        """
        raise NotImplemented("this function not implemented 'BaseInstall.install'")


class BinaryInstall(BaseInstall):
    """
    实现二进行包的安装
    """
    logger = logger.getChild("BinaryInstall")
    _pkg_repo_dir = "/usr/local/dbm-agent/pkg/"
    _install_dir = "/usr/local/"

    def __init__(self,linux_user_name="dbma", pkg=None ):
        """
        Parameters:
        -----------
        linux_user_name: str 
            守护进程的用户名

        pkg: str
            安装包的名称
        
        """
        self._linux_user, self._linux_group = self.user_and_group_factory(linux_user_name)
        self._pkg = pkg
        # 标准默认值

    def check_is_pkg_exists(self):
        """
        检查安装包是否存在

        Returns:
        -------
            bool
        """
        logger = self.logger.getChild("check_is_pkg_exists")
        logger.info(f"going to check pkg {self._pkg} ")

        # 确认是否存在
        pkg_full_path = fs.join(self._pkg_repo_dir,self._pkg)
        result =  fs.is_file_exists(pkg_full_path)

        logger.info(f"pkg exists = {result} ")
        return result

    def create_user(self):
        """
        创建用户(user.create 当用户存在的时候就不会创建)
        """
        logger = self.logger.getChild("create_user")
        logger.info(f"going to create user {str(self._linux_user)} ")

        # 创建用户
        self._linux_user.create()

        logger.info(f"done ")

    def extract_pkg(self):
        """
        解压安装包
        """
        # 把安装包(/usr/local/dbm-agent/pkg/xxx.yyy)   解压到 安装目录(/usr/local/)
        fs.extract_tar_file(fs.join(self._pkg_repo_dir, self._pkg), self._install_dir)

    def install(self):
        """
        二进制包的安装流程
        """
        with sudos.sudo():
            is_exists = self.check_is_pkg_exists()
            if not is_exists:
                raise Exception(f"pkg {self._pkg} not exists in /usr/local/dbm-agent/pkgs/ ")
            self.create_user()
            self.extract_pkg()
            self.make_link()
            self.chown()
            self.exports()
