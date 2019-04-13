import os
import shutil
from collections import namedtuple
from unittest import TestCase
from dbma.config import get_config_from_file
from dbma.init import init_dbma
from dbma.utils import users

class GetConfigFromFileTestCase(TestCase):
    """
    测试 get_config_from_file 函数
    """
    

    def setUp(self):
        """
        配置测试环境，由于要生成配置文件所以要执行 init 操作
        """
        Args = namedtuple('Args',['user','dbmc_site','log_file','config_file','basedir'])
        args = Args('dbma','https://192.168.100.10','logs/dbm-agent.log','etc/dbma.cnf','/usr/local/dbm-agent')
        # 由于执行了 init_dbma 所以 setUp 的时候会执行一次完整的“初始化”
        init_dbma(args)
        self.args = args

    def test_001_config_file_include_dbmc_site(self):
        config_file_full_path = os.path.join(self.args.basedir,self.args.config_file)
        parser = get_config_from_file(config_file_full_path)
        self.assertTrue('dbma' in parser.sections())

    def tearDown(self):
        with users.sudo('su root for rm /usr/local/dbm-agent'):
            shutil.rmtree(self.args.basedir)


    
        
