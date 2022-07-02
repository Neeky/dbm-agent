# -*- coding: utf8 -*-
"""
实现操作系统用户的相关操作
"""

import pwd
import grp
from dbma.bil.cmdexecutor import exe_shell_cmd
from dbma.loggers.loggers import get_logger

logger = get_logger(__file__)


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


class Identify(object):
    """
    """
    logger = logger.getChild("Identify")
    _not_implement_message = "please impolement it in sub class ."

    # 标识名(用户名 | 组名)
    name = ''

    def __init__(self, name):
        """
        """
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
        logger = self.logger.getChild("create")
        logger.info(f"go to create os user {self.name}")

        if self.is_exists():
            return
        exe_shell_cmd(self.create_shell_str())

        logger.info(f"os user {self.name} created")

    def drop(self):
        """删除用户|属组

        Return
        ------
            None
        """
        if self.is_exists():
            exe_shell_cmd(self.drop_shell_str())


class BaseGroup(Identify):
    """所有操作系统用户属组的基类
    """

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

    __str__ = __repr__


class BaseUser(Identify):
    """所有用户的基类
    """
    group = None
    home = ''

    def __init__(self, name, group='nobody', home=''):
        Identify.__init__(self,name)

        # 把 group 设置为 BaseGroup 的对象
        if isinstance(group,str):
            self.group = BaseGroup(group)
        else:
            self.group = group
        
        # 添加定制 home-dir 的支持
        self.home = home
        self.name = name

    def create_shell_str(self) -> str:
        if self.home == '':
            return f"useradd {self.name} -g {self.group.name}"
        else:
            return f"useradd {self.name} -g {self.group.name} -d {self.home}"
    
    def drop_shell_str(self) -> str:
        return f"userdel {self.name}"

    def is_exists(self):
        return is_user_exists(self.name)


class MySQLGroup(BaseGroup):
    def __init__(self,name="mysql"):
        BaseGroup.__init__(self,name)


class MySQLUser(BaseUser):
    """
    """
    # MySQL 端口
    port = 3306
    group = MySQLGroup()

    def __init__(self,port:int=3306):
        """根据 MySQL 监听的端口创建用户

        Parameter
        ---------
            port: int
        """
        self.name = f"mysql{port}"
        self.port = port
        BaseUser.__init__(self,self.name,group=self.group)
    
    def create(self):
        """创建 MySQL 实例用户(如果属组不存在就先创建属组)
        """
        if self.group.is_exists() == False:
            self.group.create()
        
        BaseUser.create(self)


class RootGroup(BaseGroup):
    """
    """
    logger = logger.getChild("RootGroup")
    
    def __init__(self, name="root"):
        BaseGroup.__init__(self,name)

    def drop(self):
        """
        root 组是不能删除的、所以这里不做任何实现
        """
        logger = self.logger.getChild("drop")
        logger.warning("root group can't be droped, skip it")
        pass

class RootUser(BaseUser):
    logger = logger.getChild("RootUser")
    
    def __init__(self):
        pass