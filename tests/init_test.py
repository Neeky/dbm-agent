import os
from dbma import init
from unittest import TestCase


class InitTestCase(TestCase):
    def setUp(self):
        Args = namedtuple('Args',['user','dbmc_site','log_file','config_file','basedir'])
        args = Args('dbma','https://192.168.100.10','logs/dbm-agent.log','etc/dbma.cnf','/usr/local/dbm-agent')
        # 由于执行了 init_dbma 所以 setUp 的时候会执行一次完整的“初始化”
        init.init_dbma(args)
        self.args = args

    def test_001_cnf_template_for_57_exists(self):
        os.path.isfile( os.path.join(self.args.basedir,'etc/cnfs/5_7.cnf.jinja') )
    
    def tearDown(self):
        init.uninit_dbma(self.args)
    




