"""
各大主流备份工具的封装
"""

import logging
from datetime import datetime
from mysql import connector


logger = logging.getLogger('dbm-agent').getChild(__name__)


class LocalClone(object):
    """
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

        except Exception as err:
            logger.error(f"backup fail inner exception: {str(err)}")
        logger.info(f"backup mysql-{self.port} complete.")
    
    backup = local_clone

        





