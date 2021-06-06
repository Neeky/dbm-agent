import unittest


from dbma.unix.stdfs import UFS

class UFSTestCase(unittest.TestCase):
    def test_001_is_file_exists(self):
        """
        """
        # 一个不存在的文件返回 False
        self.assertFalse(UFS.is_file_exists("/tmmp/hellos-istsighseis.log"))

        # 一个存在的文件返回 True
        self.assertTrue(UFS.is_file_exists("/etc/passwd"))

