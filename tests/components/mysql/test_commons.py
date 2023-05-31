# -*- coding: utf8 -*-

import unittest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path

from dbma.components.mysql.commons import get_mysql_version, pkg_to_basedir


# region get_mysql_version


class GetMySQLVersionTestCase(unittest.TestCase):
    """ """

    def test_get_mysql_version_given_correct_mysql_pkg(self):
        """
        given: 给定的 MySQL 安装包名正确
        when: 调用  get_mysql_version()
        then: 返回版本号
        """
        version = get_mysql_version("mysql-8.0.33-linux-glibc2.28-x86_64.tar.gz")
        expected = "8.0.33"
        self.assertEqual(version, expected)

        version = get_mysql_version("mysql-5.7.7-linux-glibc2.28-x86_64.tar.gz")
        expected = "5.7.7"
        self.assertEqual(version, expected)

    def test_get_mysql_version_given_incorrect_mysql_pkg(self):
        """
        given: 给定的 MySQL 安装包名不正确
        when: 调用  get_mysql_version()
        then: 返回版本号
        """
        version = get_mysql_version("mysql-x.x.xx-linux-glibc2.28-x86_64.tar.gz")
        expected = None
        self.assertEqual(version, expected)


# endregion get_mysql_version


# region pkg_to_basedir


class PkgToBasedirTestCase(unittest.TestCase):
    def test_pkg_to_basedir(self):
        pkg = Path("mysql-8.0.33-linux-glibc2.28-x86_64.tar.gz")
        basedir = Path("/usr/local/mysql-8.0.33-linux-glibc2.28-x86_64")
        self.assertEqual(pkg_to_basedir(pkg), basedir)


# endregion pkg_to_basedir
