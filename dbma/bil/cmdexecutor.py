# -*- coding: utf8 -*-

"""
执行命令行相关的操作都在这里完成
"""

import subprocess
from dbma.bil.sudos import sudo


def exe_shell_cmd(cmd: str):
    """以 root 身份执行命令

    Parameter
    ---------
        cmd:str 要执行的命令

    Return
    ------
        None
    """
    with sudo():
        subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
