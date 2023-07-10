# -*- coding: utf8 -*-

import unittest
from unittest.mock import Mock, patch, MagicMock, call, mock_open
from pathlib import Path

from dbma.components.mysql.config import MySQLConfig


class MySQLConfigTestCase(unittest.TestCase):
    """
    MySQL 配置文件生成类的测试
    """

    basedir = "mysql-8.0.33-linux-glibc2.28-x86_64"
    port = 3333
    innodb_buffer_pool_size = "128M"

    def test_version_given_an_normal_cnf(self):
        """
        given: 创建一个 MySQLConfig 的实例
        then: 它的 version 属性值将与 basedir 中的版本号保持一致
        """
        cnf = MySQLConfig(self.basedir, self.port, self.innodb_buffer_pool_size)
        self.assertEqual(cnf.version, "8.0.33")

    @patch.object(Path, "exists")
    def test_save_to_target_dir_given_dir_exists(self, mock_exists):
        """
        given: 给定一个 MySQLConfig 的实例, 给定一个存在的目录
        when: 调用它的 save_to_target_dir 函数
        then: 会把配置项以 json 的形式，保存到文件中
        """
        mock_exists.return_value = True
        cnf = MySQLConfig(self.basedir, self.port, self.innodb_buffer_pool_size)
        with patch("dbma.components.mysql.config.open", mock_open(read_data="x")) as m:
            cnf.save_to_target_dir(Path("/tmp/"))
            # 断言它有以写的方式打开文件
            m.assert_called_with(Path("/tmp/mysql-config.json"), "w")

    @patch.object(Path, "exists")
    def test_save_to_target_dir_given_dir_not_exists(self, mock_exists):
        """
        given: 给定一个 MySQLConfig 的实例, 给定一个不存在的目录
        when: 调用它的 save_to_target_dir 函数
        then: 不会打开任命文件进行写入操作
        """
        mock_exists.return_value = False
        cnf = MySQLConfig(self.basedir, self.port, self.innodb_buffer_pool_size)
        with patch("dbma.components.mysql.config.open", mock_open(read_data="x")) as m:
            cnf.save_to_target_dir(Path("/tmp/"))
            # 断言它有以写的方式打开文件
            m.assert_not_called()
