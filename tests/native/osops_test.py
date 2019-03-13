import unittest
import pwd
import os
from native.osops import sudo,OSOperator
from native.actions import AgentInit


class SudoTestCase(unittest.TestCase):
    """
    """
    def setUp(self):
        try:
            dbma_uid = pwd.getpwnam('dbma')[2]
        except KeyError:
            AgentInit.create_user('dbma',2233)
            dbma_uid = 2233

        self.dbma_uid = dbma_uid
        os.seteuid(self.dbma_uid)

    def test_sudo_001(self):
        """测试 sudo 上下文件管理器是否正常
        """
        # 当前权限为普通用户
        self.assertEqual(os.geteuid(),self.dbma_uid)

        with sudo():
            self.assertEqual(os.geteuid(),0)
        # 当前权限为普通用户
        self.assertEqual(os.geteuid(),self.dbma_uid)


class OSOperatorTestCase(unittest.TestCase):
    """对 OSOperation 类进行测试
    """

        
