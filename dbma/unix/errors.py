# 操作系统用户相关的异常
class OSUserException(Exception):
    pass


class UserNotExistsException(OSUserException):
    pass


class UserHasExistsException(OSUserException):
    pass


class GroupNotExistsException(OSUserException):
    pass

# 文件系统相关的异常

class FSException(Exception):
    pass


class FileNotExistsException(FSException):
    pass