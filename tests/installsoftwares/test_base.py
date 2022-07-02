# -*- coding: utf8 -*-
"""
对于软件安装环节各个功能的测试
"""

import unittest
from unittest.mock import MagicMock


class UserAndGroupFactoryTestCase(unittest.TestCase):
    """
    检查根据用户名能否返回正确的用户和组
    """
    def test_given_root_when_call_user_and_group_factory_then_return_rootuser_root_group(self):
        """
        given: 当给定的用户名是 root
        when: 调用 user_and_group_factory 方法
        then: 返回 RootUser & RootGroup
        """
        from dbma.bil.osuser import RootUser, RootGroup
        from dbma.installsoftwares.base import BaseInstall

        base_install = BaseInstall()
        user, group = base_install.user_and_group_factory("root")
        self.assertIsInstance(user, RootUser)
        self.assertIsInstance(group, RootGroup)
        self.assertTrue(str(user), "root:root")

    def test_given_mysql_when_call_user_and_group_factory_then_return_mysqluser_mysqlgroup(self):
        """
        given: 当给定的用户名是 mysql
        when: 调用 user_and_group_factory 方法
        then: 返回 MysqlUser & MysqlGroup
        """
        from dbma.bil.osuser import MySQLUser, MySQLGroup
        from dbma.installsoftwares.base import BaseInstall

        base_install = BaseInstall()
        user, group = base_install.user_and_group_factory(3306)
        self.assertIsInstance(user, MySQLUser)
        self.assertIsInstance(group, MySQLGroup)
        self.assertEqual(str(user), "mysql3306:mysql")
    

class BinaryInstallTestCase(unittest.TestCase):
    """
    """
    def test_given_pkg_and_user_when_call_install_then_do_install_procedure(self):
        from dbma.installsoftwares.base import BinaryInstall
        bi = BinaryInstall("root",pkg="TencentKona-17.0.3.b1-jdk_linux-x86_64.tar.gz")
        bi.check_is_pkg_exists = MagicMock(return_value=True)
        bi.create_user = MagicMock(return_value=None)
        bi.extract_pkg = MagicMock(return_value=None)
        bi.make_link = MagicMock(return_value=None)
        bi.chown = MagicMock(return_value=None)

        bi.install()

        bi.check_is_pkg_exists.assert_called_once()
        bi.create_user.assert_called_once()
        bi.extract_pkg.assert_called_once()
        bi.make_link.assert_called_once()
        bi.chown.assert_called_once()