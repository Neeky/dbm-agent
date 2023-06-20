# -*- coding: utf8 -*-

import os
import unittest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
from collections import namedtuple

from dbma.bil.fs import get_file_size, is_file_greater_then, truncate_or_delete_file


# region get_file_size
class GetFileSizeTestCase(unittest.TestCase):
    @patch("os.lstat")
    def test_get_file_size(self, mock):
        """ """
        StatResult = namedtuple("StatResult", "st_size")
        mock.return_value = StatResult(128 * 1024 * 1024)

        expected = 128 * 1024 * 1024
        result = get_file_size("/tmp/a.txt")
        self.assertEqual(expected, result)


# endregion get_file_size


# region is_file_greater_then


class IsFileGreaterThenTestCase(unittest.TestCase):
    """ """

    file_name = "/tmp/big-file.txt"

    @patch("dbma.bil.fs.get_file_size")
    def test_is_file_greater_then_given_file_greater(self, mock):
        """
        given: 给定的文件比 16MB 要大
        when: 调用 is_file_greater_then
        then: 返回 True
        """
        mock.return_value = 8 * 1024 * 1024

        result = is_file_greater_then(self.file_name, 16 * 1024 * 1024)
        self.assertEqual(result, False)


# endregion is_file_greater_then


# region truncate_or_delete_file
class TruncateOrDeleteFileTestCase(unittest.TestCase):
    @patch("os.remove")
    @patch("dbma.bil.fs.get_file_size")
    @patch("os.truncate")
    def test_truncate_or_delete_file_given_file_greater_then_chunk_size(
        self, mock_truncate, mock_get_file_size, mock_remove
    ):
        """
        given: 给定的文件大于 chunk_size
        when: 调用 truncate_or_delete_file
        then: 执行 truncate 操作
        """
        mock_get_file_size.return_value = 17 * 1024 * 1024
        truncate_or_delete_file("/tmp/xxx.txt", 16 * 1024 * 1024)

        mock_truncate.assert_called_once()
        mock_remove.assert_not_called()

    @patch("os.remove")
    @patch("dbma.bil.fs.get_file_size")
    @patch("os.truncate")
    def test_truncate_or_delete_file_given_file_less_then_chunk_size(
        self, mock_truncate, mock_get_file_size, mock_remove
    ):
        """
        given: 给定的文件小于 chunk_size
        when: 调用 truncate_or_delete_file
        then: 执行 remove 操作
        """
        mock_get_file_size.return_value = 15 * 1024 * 1024
        truncate_or_delete_file("/tmp/xxx.txt", 16 * 1024 * 1024)

        mock_truncate.assert_not_called()
        mock_remove.assert_called_once()


# endregion truncate_or_delete_file
