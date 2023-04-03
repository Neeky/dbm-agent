# -*- coding: utf8 -*-

"""
测试 cmdexecutor.py 模块
"""

import subprocess
from pytest_mock import MockerFixture
from dbma.bil.cmdexecutor import exe_shell_cmd

class TestCmdExcutor(object):
    def test_exe_shell_cmd(self, mocker: MockerFixture):
        mocker.patch("subprocess.run")
        exe_shell_cmd("ls -lh /tmp/")
        subprocess.run.assert_called_once_with('ls -lh /tmp/', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        