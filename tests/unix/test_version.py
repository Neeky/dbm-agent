"""
实现对版本号相关逻辑的测试

# (c) 2019, LeXing Jinag <neeky@live.com 1721900707@qq.com https://www.sqlpy.com/>
# Copyright: (c) 2019, dbm Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""


import re
from unittest import TestCase

from dbma.unix.version import DBM_AGENT_MAJOR_VERSION,DBM_AGENT_MINOR_VERSION
from dbma.unix.version import DBM_AGENT_VESION,DEFAULT_MYSQL_VERSION


class AgentVersionTestCase(TestCase):
    """
    """
    def test_minor_version(self):
        """
        检查 minor version 一定要是大于 24 的
        """
        self.assertTrue(DBM_AGENT_MINOR_VERSION > 24)

    def test_major_version(self):
        """
        检查 major version 一定要大于等于 8 
        """
        self.assertTrue(DBM_AGENT_MAJOR_VERSION >= 8)

    def test_mysql_default_pkg_version(self):
        """
        检查 dbm-agent 的主、次 版本号与 MySQL 的版本号是否对应
        """
        self.assertTrue(f"{DBM_AGENT_MAJOR_VERSION}.0.{DBM_AGENT_MINOR_VERSION}" in DEFAULT_MYSQL_VERSION)