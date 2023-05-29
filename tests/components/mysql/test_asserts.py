# -*- coding: utf8 -*-

import unittest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path

from dbma.components.mysql.asserts import (
    assert_mysql_install_pkg_exists,
    assert_mysql_datadir_not_exists,
    assert_mysql_systemd_file_exists,
    assert_mysql_systemd_file_not_exists,
)
from dbma.components.mysql.exceptions import (
    MySQLPkgFileNotExistsException,
    MySQLDataDirectoryExists,
    MySQLSystemdFileNotExists,
    MySQLSystemdFileExists,
)


class MySQLInstallPkgTestCase(unittest.TestCase):
    def test_assert_mysql_install_pkg_exists_given_pkg_not_exists(self):
        """
        given: 安装包不存在
        when: 调用 assert_mysql_install_pkg_exists(pkg)
        then: 报 MySQLPkgFileNotExistsException 异常
        """
        mock = Mock(name="Mock-Path")
        mock.is_absolute.return_value = False
        mock.exists.return_value = False
        with self.assertRaises(MySQLPkgFileNotExistsException):
            assert_mysql_install_pkg_exists(mock)

    def test_assert_mysql_install_pkg_exists_given_pkg_exists(self):
        """
        given: 安装包不存在
        when: 调用 assert_mysql_install_pkg_exists(pkg)
        then: 不会报异常
        """
        mock = Mock(name="Mock-Path")
        mock.is_absolute.return_value = False
        mock.exists.return_value = True
        # 不会有异常
        assert_mysql_install_pkg_exists(mock)


class MysqlDatadirNotExists(unittest.TestCase):
    def test_assert_mysql_datadir_not_exists_given_datadir_not_exists(self):
        """
        given: 数据目录不存在
        when: 调用 assert_mysql_install_pkg_exists(3306)
        then: 正常返回不报异常
        """
        with patch.object(Path, "exists") as mock:
            mock.return_value = False
            assert_mysql_datadir_not_exists()

    def test_assert_mysql_datadir_not_exists_given_datadir_exists(self):
        """
        given: 数据目录不存在
        when: 调用 assert_mysql_install_pkg_exists(3306)
        then: 正常返回不报异常
        """
        with patch.object(Path, "exists") as mock:
            mock.return_value = True
            with self.assertRaises(MySQLDataDirectoryExists):
                assert_mysql_datadir_not_exists(3306)


class MysqlSystemdFileTestCase(unittest.TestCase):
    def test_assert_mysql_systemd_file_exists_given_exists(self):
        """
        given: systemd 文件存在的情况
        when: 调用 assert_mysql_systemd_file_exists
        then: 正常返回不报异常
        """
        with patch.object(Path, "exists") as mock:
            mock.return_value = True
            assert_mysql_systemd_file_exists(3306)

    def test_assert_mysql_systemd_file_exists_given_file_not_exists(self):
        """
        given: systemd 文件不存在的情况
        when: 调用 assert_mysql_systemd_file_exists
        then: 报 MySQLSystemdFileNotExists 异常
        """
        with patch.object(Path, "exists") as mock:
            mock.return_value = False
            with self.assertRaises(MySQLSystemdFileNotExists):
                assert_mysql_systemd_file_exists(3306)

    def test_assert_mysql_systemd_file_not_exists_given_not_exists(self):
        """
        given: systemd 文件不存在的情况
        when: 调用 assert_mysql_systemd_file_not_exists
        then: 正常返回不报异常
        """
        with patch.object(Path, "exists") as mock:
            mock.return_value = False
            assert_mysql_systemd_file_not_exists(3306)

    def test_assert_mysql_systemd_file_not_exists_given_exists(self):
        """
        given: systemd 文件存在的情况
        when: 调用 assert_mysql_systemd_file_not_exists
        then: 报 MySQLSystemdFileExists 异常
        """
        with patch.object(Path, "exists") as mock:
            mock.return_value = True
            with self.assertRaises(MySQLSystemdFileExists):
                assert_mysql_systemd_file_not_exists(3306)
