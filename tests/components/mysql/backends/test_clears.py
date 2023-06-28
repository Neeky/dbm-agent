# -*- coding: utf8 -*-

import os
import unittest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
from datetime import datetime
from dbma.components.mysql.backends.clears import ClearTask, scan_data_dir_gen_task


# region scan_data_dir_gen_task
class ScanDirsGenTaskTestCase(unittest.TestCase):
    """ """

    @patch("glob.glob")
    def test_scan_data_dir_gen_task_given_no_instance_expired(self, mock):
        """
        given: 在没有过期实例的环境下调用
        when: 调用 scan_data_dir_gen_task
        then: /database/mysql/data/*, /database/mysql/binlog/* 这两个地方都要被扫一次
        """
        a_to_v = {
            "/database/mysql/data/*": [
                "/database/mysql/data/3309",
            ],
            "/database/mysql/binlog/*": [
                "/database/mysql/binlog/3309",
            ],
        }

        def side_effect(a):
            return a_to_v[a]

        mock.side_effect = side_effect

        tasks = scan_data_dir_gen_task()

        calls = [call("/database/mysql/data/*"), call("/database/mysql/binlog/*")]
        self.assertEqual(mock.call_args_list, calls)
        # 由于没有过期等待清理的实例，所以这个要返回 []
        self.assertEqual(tasks, [])

    @patch("glob.glob")
    def test_scan_data_dir_gen_task_given_has_instance_expired(self, mock):
        """
        given: 预期的调用环境下
        when: 调用 scan_data_dir_gen_task
        then: /database/mysql/data/*, /database/mysql/binlog/* 这两个地方都要被扫一次
        """
        a_to_v = {
            "/database/mysql/data/*": [
                "/database/mysql/data/3308-backup-2023-05-29T20-23-32-000000",
            ],
            "/database/mysql/binlog/*": [
                "/database/mysql/binlog/3308-backup-2023-05-29T20-23-32-000000",
            ],
            "/database/mysql/data/3308-backup-2023-05-29T20-23-32-000000/*": [],
            "/database/mysql/binlog/3308-backup-2023-05-29T20-23-32-000000/*": [],
        }

        def side_effect(a):
            return a_to_v[a]

        mock.side_effect = side_effect

        tasks = scan_data_dir_gen_task()

        calls = [
            call("/database/mysql/data/*"),
            call("/database/mysql/data/3308-backup-2023-05-29T20-23-32-000000/*"),
            call("/database/mysql/binlog/*"),
            call("/database/mysql/binlog/3308-backup-2023-05-29T20-23-32-000000/*"),
        ]
        self.assertEqual(mock.call_args_list, calls)
        # binlog 目录和 datadir 目录都要清理所以最终的结果应该是 2
        self.assertEqual(len(tasks), 2)


# endregion scan_data_dir_gen_task


# region ClearTask
class ClearTaskTestCase(unittest.TestCase):
    path = "/database/mysql/data/3308-backup-2023-05-29T20-23-32-000000"
    files = ["my.cnf", "ibdata1.idb", "mysql"]

    def test__init(self):
        task = ClearTask(self.path)

    def test_is_expired_given_dir_expired(self):
        """
        given: 给定的备份目录已经过期
        when: 调用 task.is_expired()
        then: 返回 True
        """
        task = ClearTask(self.path)
        self.assertEqual(task.is_expired(), True)

    def test_is_expired_given_dir_not_expired(self):
        """
        given: 给定的备份目录没有过期
        when: 调用 task.is_expired()
        then: 返回 False
        """
        task = ClearTask(self.path)
        now = datetime(2023, 5, 30, 0, 0, 0)
        self.assertEqual(task.is_expired(now), False)

    def test_glob(self):
        """
        given: 给定一个 task 对象
        when: 调用 glob
        then: 返回 task.path 下所有的文件和目录
        """
        task = ClearTask(self.path)
        expected = []
        for item in self.files:
            _path = os.path.join(self.path, item)
            expected.append(_path)
        task.glob = Mock(return_value=expected)
        self.assertEqual(expected, task.glob())


# endregion ClearTask
