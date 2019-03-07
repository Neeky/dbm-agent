import unittest
import os.path
from linuxkits import environment


class EnvironmentTestCase(unittest.TestCase):
    """把 data/profile 文件复制到 data/profile_temp 以用于测试
    """
    def setUp(self):
        current_dir = os.path.dirname(__file__)
        profile_template_file = os.path.join(current_dir,'data/profile')

        # 读出 data/profile 中的内容到 chunk 中
        with open(profile_template_file,'br') as ptf:
            chunk = ptf.read()
        
        # 把 chunk 中的内容写到 data/profile_temp
        profile_temp = os.path.join(current_dir,'data/profile_temp')
        with open(profile_temp,'bw') as profile_temp_f:
            profile_temp_f.write(chunk)
        
        self.profile=profile_temp
        super().setUp()

    def tearDown(self):
        """清理 data/profile_temp 文件
        """
        os.remove(self.profile)
        super().tearDown()

    def test_edit_path_env_for_insert(self):
        """测试向 profile 中导入环境变量看是否成功
        """
        environment.edit_path_env(profile=self.profile,value='/usr/local/mysql/bin/',action='insert')
        with open(self.profile) as profile_temp:
            self.assertIn('export PATH=/usr/local/mysql/bin/:$PATH\n',profile_temp)

    def test_edit_path_env_for_delete(self):
        environment.edit_path_env(profile=self.profile,value='/usr/local/mysql/bin/',action='delete')
        with open(self.profile) as profile_temp:
            self.assertNotIn('export PATH=/usr/local/mysql/bin/:$PATH\n',profile_temp)


