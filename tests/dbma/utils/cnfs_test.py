"""
针对 dbma.utils.cnfs 的各项功能进行测试
"""
import os
import unittest
import psutil
from dbma.utils import cnfs,users

cpu_cores = psutil.cpu_count()
mem_size,*_= psutil.virtual_memory()
mem_size = int(mem_size/(1000 * 1000))

for disk in psutil.disk_partitions():
    if disk.mountpoint == 'databases/':
        disk_size,*_ = psutil.disk_usage(disk.mountpoint)
        break
    elif disk.mountpoint == 'data/':
        disk_size,*_ = psutil.disk_usage(disk.mountpoint)
        break
else:
    disk_size,*_ = psutil.disk_usage('/')

disk_type = 'SSD'

#mysql_version = 'mysql-5.7.22-linux-glibc2.12-x86_64'

class Cnf57TestCase(unittest.TestCase):
    def setUp(self):
        self.cpu_cores = cpu_cores
        self.mem_size = mem_size
        self.disk_size = disk_size
        self.disk_type = disk_type
        self.mysql_version = 'mysql-5.7.22-linux-glibc2.12-x86_64'
        self.cnf = cnfs.mysql_auto_config(self.cpu_cores,self.mem_size,self.disk_size,self.disk_type,self.mysql_version)
        self.cnfpath = f'/etc/my{self.cnf.port}.cnf'
        self.systemdpath = f'/usr/lib/systemd/system/mysqld{self.cnf.port}.service'
    
    def test_001_write_cnf_file(self):
        self.cnf.write_cnf_file()
        self.assertTrue(os.path.isfile(self.cnfpath))

    def test_002_write_mysqld_file(self):
        self.cnf.write_mysqld_file()
        self.assertTrue(os.path.isfile(self.systemdpath))
    
    def tearDown(self):
        with users.sudo(f'su root for delete {self.cnfpath},{self.systemdpath}'):
            if os.path.exists(self.cnfpath):
                os.remove(self.cnfpath)
            if os.path.exists(self.systemdpath):
                os.remove(self.systemdpath)


class Cnf80TestCase(unittest.TestCase):
    def setUp(self):
        self.cpu_cores = cpu_cores
        self.mem_size = mem_size
        self.disk_size = disk_size
        self.disk_type = disk_type
        self.mysql_version = 'mysql-8.0.14-linux-glibc2.12-x86_64'
        self.cnf = cnfs.mysql_auto_config(self.cpu_cores,self.mem_size,self.disk_size,self.disk_type,self.mysql_version)
        self.cnfpath = f'/etc/my{self.cnf.port}.cnf'
        self.systemdpath = f'/usr/lib/systemd/system/mysqld{self.cnf.port}.service'
    
    def test_001_write_cnf_file(self):
        self.cnf.write_cnf_file()
        self.assertTrue(os.path.isfile(self.cnfpath))

    def test_002_write_mysqld_file(self):
        self.cnf.write_mysqld_file()
        self.assertTrue(os.path.isfile(self.systemdpath))
    
    def tearDown(self):
        with users.sudo(f'su root for delete {self.cnfpath},{self.systemdpath}'):
            if os.path.exists(self.cnfpath):
                os.remove(self.cnfpath)
            if os.path.exists(self.systemdpath):
                os.remove(self.systemdpath)
        


    
    

    



