# -*- coding: utf8 -*-

import unittest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import PosixPath
from dbma.components.mysql.install import create_init_sql_file


# region create_init_sql_file
class CreateInitSQLFileTestCase(unittest.TestCase):
    # 不管是哪个版本的 MySQL 用户初始化文件都是一个
    dest = "/tmp/mysql-init-user.sql"

    @patch("shutil.copy")
    def test_create_init_sql_file_given_8_0_x_version(self, mock):
        """
        given: 当给定的 MySQL 版本号是 MySQL-8.0.x 版本的话，就复制 init-8.0.x.sql 到 /tmp/
        when: 调用 create_init_sql_file
        then: shutil.copy 会复制对应的文件到 /tmp/
        """
        src = PosixPath("/data/repos/dbm-agent/dbma/static/cnfs/init-8.0.x.sql")
        # dest = "/tmp/mysql-init-user.sql"
        create_init_sql_file("8.0.23")
        mock.assert_called_once()
        mock.assert_called_once_with(src, self.dest)

    @patch("shutil.copy")
    def test_create_init_sql_file_given_5_7_x_version(self, mock):
        """
        given: 当给定的 MySQL 版本号是 MySQL-5.7.x 版本的话，就复制 init-5.7.x.sql 到 /tmp/
        when: 调用 create_init_sql_file
        then: shutil.copy 会复制对应的文件到 /tmp/
        """
        src = PosixPath("/data/repos/dbm-agent/dbma/static/cnfs/init-5.7.x.sql")
        create_init_sql_file("5.7.44")
        mock.assert_called_once()
        mock.assert_called_once_with(src, self.dest)

    @patch("shutil.copy")
    def test_create_init_sql_file_given_error_version(self, mock):
        """
        given: 当给定的 MySQL 版本号是不被支持的
        when: 调用 create_init_sql_file
        then: shutil.copy 就不会被调用并且报 ValueError
        """
        src = PosixPath("/data/repos/dbm-agent/dbma/static/cnfs/init-5.7.x.sql")
        with self.assertRaises(ValueError):
            create_init_sql_file("8848.10086.10000")

        mock.assert_not_called()


# endregion create_init_sql_file
