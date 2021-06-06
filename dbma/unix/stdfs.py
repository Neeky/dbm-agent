"""
实现文件系统相关的功能
"""

import os
from dbma.loggers.loggers import unix_logger
from dbma.unix.errors import FileNotExistsException


logger = unix_logger.getChild("stdfs")

class UFS(object):
    """
    """
    logger = logger.getChild("UFS")

    @classmethod
    def is_file_exists(cls,file_path:str="/var/log/message")->bool:
        """
        检查文件是否存在


        file_path
        ---------
            str: 文件全路径

        return
        ------
            bool
        """
        
        if os.path.isfile(file_path) == False:
            cls.logger.warning(f"file '{file_path}' not exists. ")
            return False

        return True
