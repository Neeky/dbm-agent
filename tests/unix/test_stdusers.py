import unittest


from dbma.unix.stdusers import LUM
from dbma.unix.errors import UserNotExistsException,UserHasExistsException,GroupNotExistsException

class LUMTestCase(unittest.TestCase):
    """
    stduser.LinuxUserManager 测试类
    """

    def test_001_is_root_exists(self):
        """
        """
        #不管怎么样 root 一定存在
        #所以这个一定是 True
        self.assertTrue(LUM.is_user_exists("root"))

    def test_002_is_xxx_exists(self):
        """
        """
        user_name = "xvxxyasijiwsb"
        self.assertFalse(LUM.is_user_exists(user_name))
        self.assertFalse(LUM.is_user_exists(""))
        self.assertFalse(LUM.is_user_exists(':'))

    def test_003_is_nobody_group_exists(self):
        """
        """
        self.assertTrue(LUM.is_group_exists("nobody"))

    def test_004_get_uid(self):
        """
        """
        with self.assertRaises(UserNotExistsException):
            LUM.get_uid("sdbasiefs")

        self.assertEqual(LUM.get_uid('root'),0)


    def test_005_get_gid(self):
        """
        """
        with self.assertRaises(GroupNotExistsException):
            LUM.get_gid("rootssves")

        gid_of_nobody = LUM.get_gid("nobody")
        self.assertEqual(type(gid_of_nobody),int)
