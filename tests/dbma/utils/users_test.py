from dbma.utils import users
import unittest

class UsersTestCase(unittest.TestCase):
    """
    针对 dbma.utils.users 中的各个函数进行测试
    """

    def setUp(self):
        """
        """
        pass
    
    def test_001_is_user_user_exists(self):
        """
        测试一个已经存在的用户
        """
        self.assertTrue(users.is_user_exists('root'))

    def test_002_is_user_user_exists(self):
        """
        测试个不存在的用户
        """
        self.assertFalse(users.is_user_exists('r5o42o91t2'))

    def test_003_is_group_exists(self):
        """
        测试一个已经存在的用户组
        """
        self.assertTrue(users.is_group_exists('root'))

    def test_004_is_group_exists(self):
        """
        测试一个不存在的用户组
        """
        self.assertFalse(users.is_group_exists('r1o2o3t49087'))

    def test_005_create_user_if_not_exists(self):
        """
        创建用户dbma，当组不存在的情况下它会把组一起给创建了
        """
        users.create_user_if_not_exists(user_name="dbma")
        self.assertTrue(users.is_user_exists("dbma"))

    def test_006_delete_user(self):
        """
        测试删除用户的方法
        """
        users.delete_user('dbma')
        self.assertFalse(users.is_user_exists('dbma'))

    def test_007_delete_group(self):
        """
        测试删除用户组的功能
        """
        self.assertTrue(users.is_group_exists('dbm'))
        users.delete_group('dbm')
        self.assertFalse(users.is_group_exists('dbm'))
        
