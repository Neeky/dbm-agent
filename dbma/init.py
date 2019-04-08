"""
用于完成 dbm-agent 的初始化
1、创建 dbmc linux 用户
2、创建 /usr/local/dbm-agent/目录和它的子目录
3、修改 /usr/local/dbm-agent/目录的权限为chomd -R dbma:dbma /usr/local/dbm-agent
"""
from dbma.utils.users import is_user_exists

def init_dbma():
    """
    """
    