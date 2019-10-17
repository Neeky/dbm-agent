import dbma
from dbma import gather
import unittest



class GatherTestCase(unittest.TestCase):
    """
    gather 模块的测试
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        pass

    @classmethod
    def tearDownClass(cls):
        super().setUpClass()
        pass

    def test_01_cpu_cores(self):
        """
        测试 cpu_cores 方法
        1、返回值一定是一个整数
        """
        self.assertIsInstance(gather.cpu_cores(),gather.CpuCores)
        self.assertIsInstance(gather.cpu_cores().counts,int)
    
    def test_02_cpu_times(self):
        """
        测试 cpu_times
        """
        self.assertIsInstance(gather.cpu_times(),gather.CpuTimes)
    
    def test_02_cpu_frequence(self):
        """
        测试 cpu_frequence
        """
        self.assertIsInstance(gather.cpu_frequence(),gather.CpuFrequency)
    




