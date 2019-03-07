import unittest
from linuxkits import existcode

class ExitCodeTestCase(unittest.TestCase):
    def test_success_code(self):
        """如果成功退出那么退出码一定要是 200
        """
        self.assertEqual(existcode.SUCCESS,200)

    def test_file_not_exist_code(self):
        """文件不存在的退出码一定要是 500
        """
        self.assertEqual(existcode.FILE_NOT_EXIST,500)

    def test_director_not_exist(self):
        """目录不存在的退出吗一定要是 501
        """
        self.assertEqual(existcode.DIRECTOR_NOT_EXIST,501)

    def test_not_support_operation(self):
        """不支持的操作退出码一定要是 600
        """
        self.assertEqual(existcode.NOT_SUPPORT_OPERATION,600)

if __name__ == "__main__":
    unittest.main()