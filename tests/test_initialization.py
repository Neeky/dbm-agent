
import os
import sys
import unittest
import dbma.initialization as initialization
import dbma.errors as errors

class InitializationTestCase(unittest.TestCase):
    """
    
    """
    def setUp(self):
        self.user = "unittest"

    def test_01_sudo(self):
        """
        在 sudo 上下文中 euid 会等于 0
        """
        with initialization.sudo("change user to root"):
            self.assertEqual(os.geteuid(),0)
            self.assertTrue(initialization.is_root(),True)

    def test_02_is_user_exists(self):
        """
        测试 is_user_exists 函数
        """
        self.assertTrue(initialization.is_user_exists('root'))
        self.assertFalse(initialization.is_user_exists('rootxeeisajes'))

    def test_03_create_user(self):
        """
        测试 create_user 函数
        """
        user = self.user
        initialization.create_user(user)
        self.assertEqual(initialization.is_user_exists(user),True)

        with self.assertRaises(errors.UserAlreadyExistsError):
            initialization.create_user(user)

    def test_04_delete_user(self):
        """
        测试 delete_user 函数
        """
        user = self.user
        initialization.delete_user(user)

        self.assertFalse(initialization.is_user_exists(user))

    def test_05_get_uid_gid(self):
        """
        """
        uid,gid = initialization.get_uid_gid('root')
        self.assertEqual(uid,0)
        self.assertEqual(gid,0)
    
    def tearDown(self):
        pass
        


    

    



    