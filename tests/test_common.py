
import shutil
import unittest
import dbma.common as common
import dbma.checkings as checkings
from datetime import datetime


class CommonTestCase(unittest.TestCase):
    """
    实现对 common 模块的测试
    """
    @classmethod
    def setUpClass(cls):
        """
        
        """
        super().setUpClass()
        cls.user_name = 'unit_user'
        cls.group_name = 'unit_group'

        cls.now = datetime.now().isoformat()
        cls.directory = f"/tmp/{cls.now}"

    @classmethod
    def tearDownClass(cls):
        """
        清理
        """
        shutil.rmtree(cls.directory)
        common.delete_user(cls.user_name)
        
    

    def test_01_create_group(self):
        """
        测试 create_group 是否正常
        """
        self.assertFalse(checkings.is_group_exists(self.group_name))
        common.create_group(self.group_name)
        self.assertTrue(checkings.is_group_exists(self.group_name))

    def test_02_create_user(self):
        """
        测试 create_user 是否正常
        """
        self.assertFalse(checkings.is_user_exists(self.user_name))
        common.create_user(self.user_name)
        self.assertTrue(checkings.is_user_exists(self.user_name))

        # 重复调用幂等
        common.create_user(self.user_name)
        self.assertTrue(checkings.is_user_exists(self.user_name))
    
    def test_03_create_direcotry(self):
        """
        测试 create_directory 是否正常
        """
        self.assertFalse(checkings.is_directory_exists(self.directory))
        common.create_directory(self.directory)
        self.assertTrue(checkings.is_directory_exists(self.directory))

        #重复调用幂等
        common.create_directory(self.directory)
        self.assertTrue(checkings.is_directory_exists(self.directory))
    
    def tset_04_delete_user(self):
        """
        """
        self.assertTrue(checkings.is_user_exists(self.user_name))
        common.delete_user(self.user_name)
        self.assertFalse(checkings.is_user_exists(self.user_name))
        
        #重复调用幂等
        common.delete_user(self.user_name)
        self.assertFalse(checkings.is_user_exists(self.user_name))    

    def test_05_delete_group(self):
        """
        实现对 delete_group 的测试
        """
        self.assertTrue(checkings.is_group_exists(self.group_name))
        common.delete_group(self.group_name)
        self.assertFalse(checkings.is_group_exists(self.group_name)) 

        #重复调用幂等
        common.delete_group(self.group_name)
        self.assertFalse(checkings.is_group_exists(self.group_name)) 

    def test_06_config_path(self):
        """
        检查 config_path 是否正确
        """
        # 一不不存在
        with open('/etc/profile') as profile:
            context = profile.read(65536)
            self.assertFalse(self.directory in context)
        # 进行配置
        common.config_path(self.directory)
        # 一定存在
        with open('/etc/profile') as profile:
            context = profile.read(65536)
            self.assertTrue(self.directory in context)


