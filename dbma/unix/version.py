DBM_AGENT_MAJOR_VERSION = 8
DBM_AGENT_MINOR_VERSION = 30
DBM_AGENT_PATCH_VERSION = 0
GLIB_VERSION = "2.12"

def _get_version_string():
    """
    返回字符串格式的版本号
    """
    return f"{DBM_AGENT_MAJOR_VERSION}.{DBM_AGENT_MINOR_VERSION}.{DBM_AGENT_PATCH_VERSION}"

def _get_default_mysql_pkg():
    """
    返回默认支持到的最新版本的 MySQL 版本号
    """
    return f"mysql-{DBM_AGENT_MAJOR_VERSION}.0.{DBM_AGENT_MINOR_VERSION}-linux-glibc{GLIB_VERSION}-x86_64.tar.xz"

# dbm-agent 版本号
DBM_AGENT_VESION = _get_version_string()
DBM_VERSION_NUMBER = DBM_AGENT_VESION
VERSION = DBM_AGENT_VESION

# 默认支持到的最新版本的 dbm-agent 版本号
DEFAULT_MYSQL_VERSION = _get_default_mysql_pkg()



