# -*- coding: utf8 -*-
"""
文件系统相关操作的测试
"""

import unittest
from unittest.mock import MagicMock, Mock

class TarFileTestCase(unittest.TestCase):
    """
    tar 解压功能的测试
    """
    def test_given_an_tar_file_when_call_extractall_then_extract_it(self):
        """
        given: 给定一个存在的 tar 文件
        when: 调用解压程序
        then: 能正确的解压文件
        """
        from dbma.bil import fs
        tar_object = Mock()
        tar_object.close = MagicMock()
        tar_object.extractall = MagicMock()
        fs.tarfile.open = MagicMock(return_value=tar_object)
        fs.extract_tar_file("/tmp/1.tar.gz","/tmp/")

        # 打开、解压、关闭 三个步骤都完成
        fs.tarfile.open.assert_called_once_with("/tmp/1.tar.gz")
        tar_object.extractall.assert_called_once_with("/tmp/")
        tar_object.close.assert_called_once()


class EtcProfileEditTestCase(unittest.TestCase):
    """ 编辑 /etc/profile 功能的测试
    """
    def test_given_line_exists_in_profile_when_call_fs_is_line_in_etc_profile_then_return_true(self):
        """
        given: 给定的行存在于 /etc/profile 中
        when:  检查行是否存在 is_line_in_etc_profile
        then:  返回 True
        """
        from dbma.bil import fs
        import os
        lines = ['export JAVA_HOME=/usr/local/java', 'export PATH=/usr/local/java/bin/:$PATH']
        os.open = MagicMock(return_value=lines)
        self.assertTrue(fs.is_line_in_etc_profile("export JAVA_HOME=/usr/local/java"))

    def test_given_line_not_exists_in_profile_when_call_fs_is_line_in_etc_profile_then_return_false(self):
        """
        given: 给定的行不存在于 /etc/profile 中
        when:  检查行是否存在 is_line_in_etc_profile
        then:  返回 False
        """
        from dbma.bil import fs
        import os
        lines = ['export JAVA_HOME=/usr/local/java', 'export PATH=/usr/local/java/bin/:$PATH']
        os.open = MagicMock(return_value=lines)
        self.assertFalse(fs.is_line_in_etc_profile("export JAVA_HOME=/usr/local/java2"))


class FileExistsTestCase(unittest.TestCase):
    """
    文件存在性检查的测试
    """
    def test_given_file_not_exists_when_call_is_file_exists_then_return_false(self):
        """

        """
        from dbma.bil import fs
        fs.os.path.exists = MagicMock(return_value=False)

        not_exists_file = "/tmp/jiang-le-xing.log"
        self.assertFalse(fs.is_file_exists(not_exists_file))
        fs.os.path.exists.assert_called_once_with(not_exists_file)


    def test_given_file_exists_when_call_is_file_exists_then_return_true(self):
        """
        """
        from dbma.bil import fs
        #fs.os.path.exists = MagicMock(return_value=True)

        exists_file = "/etc/profile"
        self.assertTrue(fs.is_file_exists(exists_file))
