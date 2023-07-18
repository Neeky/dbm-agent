# -*- coding: utf8 -*-

import unittest
from unittest.mock import Mock, patch, MagicMock, call, mock_open
from pathlib import Path

from dbma.components.mysql.config import (
    MySQLSystemdConfig,
    MySQLSRConfig,
)


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


class MySQLSRConfigTestCase(unittest.TestCase):
    """ """

    port = 3306
    basedir = "/usr/local/mysql-8.0.33-linux-glibc2.28-x86_64"

    def test_config_template_path_given_port_3306(self):
        """ """
        cnf = MySQLSRConfig(3306, "/usr/local/mysql-8.0.33/", "128M")
        self.assertEqual(cnf.user, "mysql3306")

    def test_save_init_cnf_given_port_3306(self):
        """ """
        cnf = MySQLSRConfig(3306, "/usr/local/mysql-8.0.33/", "128M")
        cnf.save = Mock()
        cnf.save_init_cnf()
        # 断言会调用两次 cnf.save()
        self.assertEqual(len(cnf.save.mock_calls), 2)

    def test_innodb_buffer_pool_instance_given_size_xx(self):
        """
        given: 给定不同的 buffer-pool-size 时
        when: 调用构造函数
        then: 验证 buffer-pool-instance 的是否匹配
        """
        # 1G -> 1
        cnf = MySQLSRConfig(3306, "/usr/local/mysql-8.0.33/", "1G")
        self.assertEqual(cnf.innodb_buffer_pool_instances, 1)

        # 0 ~ 2G -> 1
        cnf = MySQLSRConfig(3306, "/usr/local/mysql-8.0.33/", "2G")
        self.assertEqual(cnf.innodb_buffer_pool_instances, 1)

        # 2 ~ 4G -> 2
        cnf = MySQLSRConfig(3306, "/usr/local/mysql-8.0.33/", "4G")
        self.assertEqual(cnf.innodb_buffer_pool_instances, 2)

        # 4G ~ 8G -> 4
        cnf = MySQLSRConfig(3306, "/usr/local/mysql-8.0.33/", "8G")
        self.assertEqual(cnf.innodb_buffer_pool_instances, 4)

        # 8G ~ 16G -> 8
        cnf = MySQLSRConfig(3306, "/usr/local/mysql-8.0.33/", "16G")
        self.assertEqual(cnf.innodb_buffer_pool_instances, 8)

        # 16+G -> 16
        cnf = MySQLSRConfig(3306, "/usr/local/mysql-8.0.33/", "20G")
        self.assertEqual(cnf.innodb_buffer_pool_instances, 16)
