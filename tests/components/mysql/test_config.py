# -*- coding: utf8 -*-

import unittest
from unittest.mock import Mock, patch, MagicMock, call, mock_open
from pathlib import Path

from dbma.components.mysql.config import (
    MySQLConfig,
    MySQLSystemdConfig,
    MySQLSystemdTemplateFileNotExists,
)


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


class MySQLSystemdConfigTestCase(unittest.TestCase):
    """ """

    port = 3306
    basedir = "/usr/local/mysql-8.0.33-linux-glibc2.28-x86_64"

    def test_user_given_port_3306(self):
        """
        given: 给定 MySQL 的端口是 3306
        when: 创建 MySQLSystemdConfig 对象
        then: 对象的 user属性应该是 mysql3306
        """
        syscnf = MySQLSystemdConfig(port=self.port, basedir=self.basedir)
        self.assertEqual("mysql3306", syscnf.user)

    @patch.object(Path, "exists")
    def test_load_given_port_3306(self, mock_exists):
        """"""
        mock_exists.return_value = True
        with patch("dbma.core.configs.open", mock_open(read_data="x")) as mock:
            syscnf = MySQLSystemdConfig(port=self.port, basedir=self.basedir)
            syscnf.load()
            # open, enter, read, exit 共四个调用
            self.assertEqual(len(mock.mock_calls), 4)
            self.assertEqual(mock.mock_calls[2], call().read())

    @patch.object(Path, "exists")
    def test_load_given_template_file_not_exists(self, mock_exists):
        """"""
        mock_exists.return_value = False
        with self.assertRaises(ValueError):
            syscnf = MySQLSystemdConfig(port=self.port, basedir=self.basedir)
            syscnf.load()

    def test_render_given_port_3306(self):
        """ """
        with patch.object(MySQLSystemdConfig, "load") as mock:
            mock.return_value = "{{user}}\n"
            syscnf = MySQLSystemdConfig(self.port, self.basedir)
            expected = "mysql3306\n"
            self.assertEqual(expected, syscnf.render())
