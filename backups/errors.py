# (c) 2019, LeXing Jiang <neeky@live.com 1721900707@qq.com https://www.sqlpy.com/>
# Copyright: (c) 2019, dbm Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


class Error(Exception):
    """
    定义所有 dbma 错误或异常基类
    """
    pass


class ExternalError(Error):
    """
    外部错误、如在调用 subprocess 时引发了异常
    """
    pass


class GroupNotExistsError(Error):
    """
    用户组不存在
    """
    pass


class UserNotExistsError(Error):
    """
    当前用户不存在
    """
    pass


class UserAlreadyExistsError(Error):
    """
    用户已经存在
    """
    pass


class FileNotExistsError(Error):
    """
    """
    pass


class FileAlreadyExistsError(Error):
    """
    """
    pass


class DirectoryNotExistsError(Error):
    """
    """
    pass


class DirecotryAlreadyExistsError(Error):
    """
    """
    pass


class NotSupportedMySQLVersionError(Error):
    """
    不支持的 MySQL 版本 目前只支持 mysql-8.0.17 及以上版本
    """
    pass


class NotSupportedPackageError(Error):
    """
    """
    pass


class DBMAIsRuningError(Error):
    """
    dbm-agent 正在运行
    """
    pass


class DBMANotInitedError(Error):
    """
    dbm-agent 还没有初始化
    """
    pass


class MySQLRestartTimeOut(Error):
    """
    MySQL restart 超时
    """
    pass


class MgrLocalAddressError(Error):
    pass


class MgrGroupSeedsError(Error):
    pass


class PortIsInUseError(Error):
    pass


class NotALocalIPError(Error):
    pass


class MySQLIsNotRunningError(Error):
    """
    当通过 127.0.0.1:${port} 连接不上 MySQL 时就可以报这个错
    """
    pass


class LocalCloneFaileError(Error):
    """
    本地克隆出错
    """
    pass


class NotSupportedZabbixAgentVersionError(Error):
    """
    不被支持的 zabbix-agent 包
    """
    pass


class NetInterfaceNotExists(Error):
    """
    给定的网卡不存在
    """
