"""
各大主流备份工具的封装
"""

import time
import logging
from datetime import datetime
from datetime import datetime
from mysql import connector
from . import checkings
from . import errors


logger = logging.getLogger('dbm-agent').getChild(__name__)


class LocalClone(object):
    """
    实现本地克隆
    """

    def __init__(self,host:str='127.0.0.1',port:str=3306,
        user:str="clone_user",password:str="dbma@0352"):
        self.host = host
        self.port = port 
        self.user = user
        self.password = password
        self.now = datetime.now().isoformat()
    
    def local_clone(self):
        """
        local clone
        """
        cnx = None
        try:
            logger.info(f"start backup mysql-{self.port} useing clone-plugin")
            cnx = connector.connect(host=self.host,port=self.port,user=self.user,password=self.password)
            cursor = cnx.cursor()
            cursor.execute(f"CLONE LOCAL DATA DIRECTORY = '/backup/mysql/{self.port}/{self.now}' ")
            # 目前 mysql-connector-python 不支持以下方案处理参数
            #cursor.execute("CLONE LOCAL DATA DIRECTORY = '/backup/mysql/%s/%s",(self.port,self.now))
        except Exception as err:
            logger.error(f"backup fail inner exception: {str(err)}")
        logger.info(f"backup mysql-{self.port} complete.")
    
    backup = local_clone
    clone = local_clone

class RemoteClone(object):
    """
    完成对远程实例的克隆
    """
    
    def __init__(self,host:str="127.0.0.1",port:int=3306,user:str="cloneuser",password="dbma@0352",
                 dhost:str="192.168.100.100",dport:int=3306,
                 cuser:str="cloneuser",cpassword:str="dbma@user",ruser="repluser",rpassword="dbma@0352"):
        self.user = user
        self.password = password
        self.host = host
        self.port = port

        self.dhost = dhost
        self.dport = dport

        self.cuser = cuser
        self.cpassword = cpassword

        self.ruser = ruser
        self.rpassword = rpassword
    
    def remonte_clone(self):
        try:
            cnx = connector.connect(host=self.host,port=self.port,user=self.user,password=self.password)
            cursor = cnx.cursor()
            # donor_list
            donor_list_sql = f"set @@global.clone_valid_donor_list='{self.dhost}:{self.dport}';"
            logger.info(donor_list_sql)
            cursor.execute(donor_list_sql)
            # clone instance from 
            # 目前 mysql-connector-python 不支持对以下语句做参数处理
            clone_sql = f"clone instance from {self.cuser}@'{self.dhost}':{self.dport} identified by '{self.cpassword}';"
            logger.info(clone_sql)
            cursor.execute(clone_sql)
        except Exception as err:
            logger.info(str(err))
        finally:
            if hasattr(cnx,'close'):
                cnx.close()
        logger.info("remonte clone complete.")
    
    def build_slave(self):
        max_wait_count = 3600
        current_wait_count = 0
        start_time = datetime.now().isoformat()
        while True:
            if checkings.is_port_in_use(self.host,self.port):
                logger.info(f"mysqld-{self.port} restart complete.")
                break

            logger.info(f"wait mysqld-{self.port} restart {current_wait_count}/{max_wait_count}")

            current_wait_count = current_wait_count + 1
            if current_wait_count == max_wait_count:
                logger.warning(f"wait mysqld-{self.port} restart time out")
                end_time = datetime.now().isoformat()
                logger.warning(f"wait mysqld-{self.port} restart from {start_time} to {end_time}")
                raise errors.MySQLRestartTimeOut()

            
            time.sleep(1)
        # sleep 11 保证 mysql 可用
        logger.info("wait 11 seconds")
        time.sleep(11)
        
        try:
            cnx = connector.connect(host=self.host,port=self.port,user=self.user,password=self.password)
            cursor = cnx.cursor()
            chnage_master_sql = f"change master to master_host='{self.dhost}',master_port={self.dport},master_user='{self.ruser}',master_password='{self.rpassword}',master_ssl = 1,master_auto_position=1;"
            logger.info(chnage_master_sql)
            # mysql-connector-python 目前还不支持这类 SQL 的参数化
            cursor.execute(chnage_master_sql)
            logger.info("change master complete.")
            start_sql = f"start slave;"
            cursor.execute(start_sql)
            logger.info(f"start slave complete.")
        except Exception as err:
            logger.error(str(err))
        finally:
            if hasattr(cnx,'close'):
                cnx.close()

    backup = remonte_clone
    clone = remonte_clone



        





