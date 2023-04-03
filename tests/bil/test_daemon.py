# -*- coding: utf8 -*-

"""
测试 bil/daemon 模块
"""

import os
import sys
import atexit
from pytest_mock import MockerFixture
from dbma.bil import daemon

class TestClassForDaemon(object):
    def test_auto_clean_pid(self, mocker: MockerFixture):
        #mocker.patch("daemon.auto_clean_pid")
        mocker.patch("os.close")
        mocker.patch("os.remove")
        daemon.auto_clean_pid(8848, "/tmp/dbm-agent.pid")
        os.close.assert_called_once_with(8848)
        os.remove.assert_called_once_with("/tmp/dbm-agent.pid")

    def test_signal_handler(self, mocker: MockerFixture):
        mocker.patch("sys.exit")
        daemon.signal_handler(2, None)
        sys.exit.assert_called_once_with(1)
    
    def test_write_pid_file(self, mocker: MockerFixture):
        mocker.patch("os.open")
        mocker.patch("fcntl.lockf")
        mocker.patch("os.truncate")
        mocker.patch("os.write")
        mocker.patch("atexit.register")
        pid = 1000
        pid_file = "/tmp/dbm-agent.pid"
        daemon.write_pid_file(pid, pid_file)
        
        os.truncate.assert_called_once()
        atexit.register.assert_called_once()