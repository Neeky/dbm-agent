"""定义全局对象，用于共享配置
"""

import re
import os
import logging

logger = logging.getLogger('dbm-agent').getChild(__name__)


class ConfigMixin(object):
    """
    """
    logger = logger.getChild("Config")
    group_name = "dbma"
    user_name = "dbma"

    pkgs_dir = "/usr/local/dbm-agent/pkg/"
    usr_local_dir = "/usr/local/"
    ld_so_dir = "/etc/ld.so.conf.d/"

    systemctl_dir = "/usr/lib/systemd/system/"
    template_dir = "/usr/local/dbm-agent/etc/templates/"

    
