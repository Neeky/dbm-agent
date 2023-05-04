# -*- coding: utf8 -*-

"""
实现操作系统用户的相关操作
"""
import logging
import os
import pwd
import grp
from dbma.bil.cmdexecutor import exe_shell_cmd
from dbma.bil.sudos import sudo


def is_root() -> bool:
    """
    检查当前的 euser 是不是 root
    """
    return os.geteuid() == 0


def is_user_exists(user: str) -> bool:
    """检查给定的用户名是否存在

    Parameter
    --------
        user: str 用户名(操作系统层面)

    Return
    ------
        bool
    """

    try:
        pwd.getpwnam(user)
        return True
    except KeyError as err:
        return False
    except TypeError as err:
        return False


def is_group_exists(group: str) -> bool:
    """检查给定的属组是否存在

    Parameter
    ---------
        group: str 属组名

    Return
    ------
        bool
    """
    try:
        grp.getgrnam(group)
        return True
    except KeyError as err:
        return False
    except TypeError as err:
        return False


def get_uid_gid(user_name):
    """
    返回给定用户的 (uid,gid) 组成的元组. 如果给定的用户不存在就返回 (0,0)
    """
    try:
        user = pwd.getpwnam(user_name)
        return user.pw_uid, user.pw_gid
    except Exception as err:
        return 0, 0


class Identify(object):
    """ """

    _not_implement_message = "please impolement it in sub class ."

    # 标识名(用户名 | 组名)
    name = ""

    def __init__(self, name):
        """ """
        self.name = name

    def create_shell_str(self) -> str:
        """返回创建对象的 shell 命令行模式

        Return
        ------
            str 返回一条可以执行的 shell 命令
        """
        raise NotImplementedError(self._not_implement_message)

    def drop_shell_str(self) -> str:
        """返回清理对象的 shell 命令行模式

        Return
        ------
            str 返回一条可以执行的 shell 命令
        """
        raise NotImplementedError(self._not_implement_message)

    def is_exists(self):
        """检查给定的标识是否存在

        Return
        ------
            bool
        """
        raise NotImplementedError(self._not_implement_message)

    def create(self):
        """创建用户|属组

        Return
        ------
            None
        """
        if self.is_exists():
            return
        exe_shell_cmd(self.create_shell_str())

    def drop(self):
        """删除用户|属组

        Return
        ------
            None
        """
        if self.is_exists():
            exe_shell_cmd(self.drop_shell_str())


class BaseGroup(Identify):
    """所有操作系统用户属组的基类"""

    def __init__(self, name):
        Identify.__init__(self, name)

    def create_shell_str(self) -> str:
        return f"groupadd {self.name}"

    def drop_shell_str(self) -> str:
        return f"groupdel {self.name}"

    def is_exists(self):
        return is_group_exists(self.name)

    def __repr__(self):
        return f"BaseGroup{{name={self.name}}}"

    def __str__(self):
        return f"{self.name}"


class BaseUser(Identify):
    """所有用户的基类"""

    group = None
    home = ""

    def __init__(self, name, home=""):
        Identify.__init__(self, name)

        # 添加定制 home-dir 的支持
        self.home = home

    def create_shell_str(self) -> str:
        if self.home == "":
            return f"useradd {self.name} -g {self.group.name}"
        else:
            return f"useradd {self.name} -g {self.group.name} -d {self.home}"

    def drop_shell_str(self) -> str:
        return f"userdel {self.name}"

    def is_exists(self):
        return is_user_exists(self.name)

    def create(self):
        """
        在创建用户的时候如果组不存在，要去创建组
        """
        if (self.group is not None) and (not self.group.is_exists()):
            self.group.create()
        Identify.create(self)

    def chown(self, path, recursive=True):
        """调用 chown 命令"""
        if recursive == True:
            cmd = f"chown -R {str(self)} {path}"
        else:
            cmd = f"chown {str(self)} {path}"
        logging.debug(cmd)
        with sudo():
            exe_shell_cmd(cmd)

    def __str__(self):
        """
        返回 user:group 的形式
        """
        return f"{self.name}:{self.group}"


class DBMAGroup(BaseGroup):
    """ """

    def __init__(self, name="dbma"):
        BaseGroup.__init__(self, name)


class DBMAUser(BaseUser):
    """ """

    group = DBMAGroup()

    def __init__(self, name="dbma"):
        BaseUser.__init__(self, name)


class MySQLGroup(BaseGroup):
    def __init__(self, name="mysql"):
        BaseGroup.__init__(self, name)


class MySQLUser(BaseUser):
    """ """

    # MySQL 端口
    port = 3306
    # 所有的 MySQL 都共用一个 MySQL 组
    group = MySQLGroup()

    def __init__(self, port: int = 3306):
        """根据 MySQL 监听的端口创建用户

        Parameter
        ---------
            port: int
        """
        self.name = f"mysql{port}"
        self.port = port
        BaseUser.__init__(self, self.name)

    def create(self):
        """创建 MySQL 实例用户(如果属组不存在就先创建属组)"""
        if self.group.is_exists() == False:
            self.group.create()

        BaseUser.create(self)

    def __str__(self):
        return f"{self.name}:{self.group}"


class RedisGroup(BaseGroup):
    """Redis 组"""

    def __init__(self, name="redis"):
        BaseGroup.__init__(self, name)


class RedisUser(BaseUser):
    """Redis 用户"""

    # Redis 端口
    port = 6379
    # 所有的 Redis 都共用一个 Redis 组
    group = RedisGroup()

    def __init__(self, port: int = 6379):
        """根据 Redis 监听的端口创建用户

        Parameter
        ---------
            port: int
        """
        self.name = f"redis{port}"
        self.port = port
        BaseUser.__init__(self, self.name)

    def create(self):
        """创建 Redis 实例用户(如果属组不存在就先创建属组)"""
        if self.group.is_exists() == False:
            self.group.create()

        BaseUser.create(self)

    def __str__(self):
        return f"{self.name}:{self.group}"


class RootGroup(BaseGroup):
    """ """

    def __init__(self, name="root"):
        BaseGroup.__init__(self, name)

    def drop(self):
        """
        root 组是不能删除的、所以这里不做任何实现
        """
        pass


class RootUser(BaseUser):
    group = RootGroup()

    def __init__(self):
        BaseGroup.__init__(self, "root")

    def drop(self):
        """
        root 组是不能删除的、所以这里不做任何实现
        """
        pass
