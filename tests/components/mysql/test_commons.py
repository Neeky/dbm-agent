# -*- coding: utf8 -*-

import unittest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path

from dbma.components.mysql.commons import (
    get_mysql_version,
    pkg_to_basedir,
    create_os_user_for_mysql,
    create_directory,
    calculate_mysql_directory_by_port_and_type,
    MySQLDirs,
    create_mysql_dirs,
)
from dbma.bil.osuser import MySQLUser
from dbma.components.mysql.exceptions import NotSuportMySQLDirectoryType


class MySQLMixIn(object):
    """ """

    port = 3306


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


# region create_os_user_for_mysql


class CreateOsUserForMysqlTestCase(unittest.TestCase, MySQLMixIn):
    """ """

    @patch("dbma.components.mysql.commons.MySQLUser")
    def test_create_os_user_for_mysql(self, mock):
        """
        given: 不管用用户存在于否
        when: 调用 create_os_user_for_mysql
        then: 调用 MySQLUser 对象的 create 方法
        """
        user = Mock()
        mock.return_value = user
        create_os_user_for_mysql(self.port)

        user.create.assert_called_once()


# endregion create_os_user_for_mysql


# region create_dir


class CreateDirectoryTestCase(unittest.TestCase, MySQLMixIn):
    def test_create_directory_given_directory_not_exists(self):
        """
        given: 当给定的目录不存在
        when: 调用 create_directory 函数
        then: 会调用  path 对象的 mkdir 方法
        """
        mock_path = Mock()
        mock_path.__class__ = Path
        mock_path.exists.return_value = False
        mock_path.parent.exists.return_value = True

        create_directory(mock_path)

        mock_path.exists.assert_called_once()
        mock_path.mkdir.assert_called_once()

    def test_create_directory_given_path_s_parent_directory_not_exists(self):
        """
        given: 当给定的父目录不存在
        when: 调用 create_directory 函数
        then: 会先创建父目录、然后再创建给定目录
        """
        mock_path = Mock()
        mock_path.__class__ = Path
        mock_path.exists.return_value = False
        mock_path.parent.exists.return_value = False
        mock_path.parent.parent.exists.return_value = True  # 爷爷路径是有的

        create_directory(mock_path)
        # 创建父目录
        mock_path.parent.mkdir.assert_called_once()
        # 创建当前目录
        mock_path.mkdir.assert_called_once()


# endregion create_dir


# region calculate_mysql_directory_by_port_and_type
class CalculateMysqlDirectoryByPortAndTypeTestCase(unittest.TestCase, MySQLMixIn):
    def test_calculate_mysql_directory_by_port_and_type(self):
        """
        given: 三种正常路径中的任何一种
        when: 调用 calculate_mysql_directory_by_port_and_type
        then: 按规范返回对应的 Path 对象
        """
        expected = Path("/database/mysql/data/3306")
        result = calculate_mysql_directory_by_port_and_type(self.port, MySQLDirs.DATA)
        self.assertEqual(expected, result)

        expected = Path("/database/mysql/binlog/3306")
        result = calculate_mysql_directory_by_port_and_type(self.port, MySQLDirs.BINLOG)
        self.assertEqual(expected, result)

        expected = Path("/database/mysql/backup/3306")
        result = calculate_mysql_directory_by_port_and_type(self.port, MySQLDirs.BACKUP)
        self.assertEqual(expected, result)

    def test_calculate_mysql_directory_by_port_and_type_given_dirtype_error(self):
        """
        given: 给定的 MySQLDirectorys 不正确
        when: 调用 calculate_mysql_directory_by_port_and_type
        then: 报异常
        """
        expected = Path("/database/mysql/data/3306")
        with self.assertRaises(NotSuportMySQLDirectoryType):
            result = calculate_mysql_directory_by_port_and_type(self.port, None)


# endregion calculate_mysql_directory_by_port_and_type


# region create_mysql_dirs


class CreateMysqlDirsTestCase(unittest.TestCase, MySQLMixIn):
    @patch("dbma.components.mysql.commons.create_directory")
    def test_create_mysql_dirs(self, mock_create_directory):
        """
        创建 MySQL 对应的目录
        """
        user = Mock()
        create_mysql_dirs(self.port, user)
        # 会调用 3 次是因为要创建 datadir backup binlog 这三个目录
        self.assertEqual(mock_create_directory.call_count, 3)
        # 3 个目录对应 3 次 chown
        self.assertEqual(user.chown.call_count, 3)


# endregion create_mysql_dirs
