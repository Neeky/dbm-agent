"""
linux 用户管理相关的通用工具
"""
import pwd

# 查询指定的用户是否存在
is_user_exists = lambda user_name: True if pwd.getpwnam(user_name) else False

def create_user_if_not_exists(user_name='dbma',uid=2049,gid=2049):
    """
    默认情况下 dbma 用户的uid 和 gid 都是 2049
    """
