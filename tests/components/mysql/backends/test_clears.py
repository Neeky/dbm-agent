# -*- coding: utf8 -*-

import os
import unittest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
from datetime import datetime
from dbma.components.mysql.backends.clears import (
    ClearTask,
    scan_data_dir_gen_task,
    clear_instance,
    start_clear_tasks,
)


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
        now = datetime(2023, 5, 29, 20, 23, 33)
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

    def test_dirs_given_an_expired_instance_only_one_dir_case(self):
        """
        given: 给定一个过期的实例，假设它只包涵 mysql 目录
        """
        # given:1 设定只有一个目录 mysql
        with patch.object(ClearTask, "glob") as mock:
            mock.return_value = [
                "/database/mysql/data/3308-backup-2000-01-01T00-00-00-000000/mysql"
            ]
            # given:1 mock 住 is_dir 让它返回 True
            with patch.object(Path, "is_dir") as path_mock:
                path_mock.return_value = True

                # 开始真正的测试
                task = ClearTask(
                    "/database/mysql/data/3308-backup-2000-01-01T00-00-00-000000"
                )
                # 1 一定是一个过期实例
                # 2 目录列表的长度应该是 1
                # 3 比较目录列表的值，应该和我们给定的一样
                self.assertEqual(task.is_expired(), True)
                self.assertEqual(len(task.dirs), 1)
                self.assertEqual(
                    task.dirs,
                    [
                        Path(
                            "/database/mysql/data/3308-backup-2000-01-01T00-00-00-000000/mysql"
                        )
                    ],
                )

    def test_dirs_given_an_expired_instance_only_one_file_case(self):
        """
        given: 给定一个过期的实例，假设它只包涵 mysql 目录
        """
        # given:1 设定只有一个 ibdata1.ibd 文件
        with patch.object(ClearTask, "glob") as mock:
            mock.return_value = [
                "/database/mysql/data/3308-backup-2000-01-01T00-00-00-000000/ibdata1.ibd"
            ]
            # given:1 mock 住 is_dir 让它返回 True
            with patch.object(Path, "is_dir") as path_mock:
                path_mock.return_value = False

                # 开始真正的测试
                task = ClearTask(
                    "/database/mysql/data/3308-backup-2000-01-01T00-00-00-000000/"
                )
                # 1 一定是一个过期实例
                # 2 文件列表的长度应该是 1
                # 3 比较文件列表的值，应该和我们给定的一样
                self.assertEqual(task.is_expired(), True)
                self.assertEqual(len(task.files), 1)
                self.assertEqual(
                    task.files,
                    [
                        Path(
                            "/database/mysql/data/3308-backup-2000-01-01T00-00-00-000000/ibdata1.ibd"
                        )
                    ],
                )

    def test_is_empty(self):
        with patch.object(ClearTask, "glob") as mock:
            mock.return_value = []
            task = ClearTask(self.path)
            self.assertEqual(task.is_empty(), True)


# endregion ClearTask


# region clear_instance
class ClearInstanceTestCase(unittest.TestCase):
    @patch("shutil.rmtree")
    def test_clear_instance_given_dir_not_empty(self, mock_rmtree):
        """
        given: 目录下没有文件、也没有目录; hack is_empty 为 False 的场景
        when: 调用 clear_instance
        then: 由于 is_empty 是 False, 所以不会调用  shutil.rmtree
        """
        mock_clear_task = Mock()
        mock_clear_task.files = []
        mock_clear_task.dirs = []
        mock_clear_task.is_empty.return_value = False

        clear_instance(mock_clear_task)

        mock_clear_task.is_empty.assert_called_once()
        mock_rmtree.assert_not_called()

    @patch("shutil.rmtree")
    def test_clear_instance_given_dir_empty(self, mock_rmtree):
        """
        given: 目录下没有文件、也没有目录; hack is_empty 为 True 的场景
        when: 调用 clear_instance
        then: 由于 is_empty 是 True, 所以会调用  shutil.rmtree
        """
        mock_clear_task = Mock()
        mock_clear_task.files = []
        mock_clear_task.dirs = []
        mock_clear_task.is_empty.return_value = True

        clear_instance(mock_clear_task)

        mock_clear_task.is_empty.assert_called_once()
        mock_rmtree.assert_called_once()

    @patch("dbma.components.mysql.backends.clears.truncate_or_delete_file")
    @patch("shutil.rmtree")
    def test_clear_instance_given_dir_empty(self, mock_rmtree, mock_tr_or_de):
        """
        given: 给定目录下只有一个文件了，并且文件小于 16MB
        when: 调用 clear_instance
        then: 文件会被清理，当前目录也会被清理
        """
        mock_clear_task = Mock()
        mock_clear_task.files = [
            "/database/mysql/data/3308-backup-2023-05-29T20-23-32-000000/ibdata1.ibd"
        ]
        mock_clear_task.dirs = []
        mock_clear_task.is_empty.return_value = True

        mock_tr_or_de.return_value = 0

        clear_instance(mock_clear_task)

        mock_clear_task.is_empty.assert_called_once()
        mock_rmtree.assert_called_once()
        mock_tr_or_de.assert_called_once_with(
            "/database/mysql/data/3308-backup-2023-05-29T20-23-32-000000/ibdata1.ibd",
            16777216,
        )


# endregion clear_instance


# region start_clear_tasks
class StartClearTasksTestCase(unittest.TestCase):
    @patch("time.sleep")
    @patch("dbma.components.mysql.backends.clears.threads.submit")
    def test_start_clear_tasks(self, mock_submit, mock_sleep):
        """
        given:
        when: 调用 start_clear_tasks
        then: 1、会调用两次 submit 2、会调用一次 sleep ，并且输入的参数是 3
        """
        start_clear_tasks()
        self.assertEqual(mock_submit.call_count, 2)
        mock_sleep.assert_called_with(3)


# endregion start_clear_tasks
