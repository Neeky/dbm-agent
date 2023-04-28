import re
from pathlib import Path

from dbma.core.configs import dbm_agent_config

# Redis 的默认端口号
default_redis_port = 6379

# 根据 dbm-agent 的配置文件确认默认情况下使用的 Redis 版本号
default_redis_pkg = Path(
    "/usr/local/dbm-agent/pkgs/redis-{}-linux-glibc-2.34-x86_64.tar.gz".format(
        dbm_agent_config.redis_default_version
    )
)

# Redis 安装包的正则表达式
redis_pkg_re_pattern = re.compile(
    r"redis-(?P<version>\d{1,2}.\d{1,2}.\d{1,3})-linux-glibc-(?P<glibc-version>\d.\d{1,2})-x86_64.tar.gz"
)
