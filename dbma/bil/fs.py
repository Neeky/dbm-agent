# -*- coding: utf8 -*-

"""
实现文件系统的相关操作
"""

import os
import tarfile


def is_file_exists(file_path):
    """
    判断文件是否存在
    """
    return os.path.exists(file_path)


def extract_tar_file(tar_file_path, extract_dir):
    """
    解压tar文件

    Parameters:
    ----------
    tar_file_path: str
        等待解压的tar文件路径

    extract_dir: str
        解压到的目标路径

    Return:
    -------
        None
    """
    tar = tarfile.open(tar_file_path)
    tar.extractall(extract_dir)
    tar.close()


def get_tar_file_name(tar_file_path):
    """
    获取tar文件的名称

    Parameters:
    -----------
    tar_file_path: str
        tar 文件的全路径

    Return:
    -------
        str
    """
    tar = tarfile.open(tar_file_path)
    name = tar.getnames()[0]
    tar.close()
    if os.sep in name:
        name, *_ = name.split(os.sep)
    return name


def link(src, dest):
    """
    创建链接

    Parameters:
    -----------
    src: str
        源路径

    dest: str
        目标路径

    Return:
    -------
        None
    """
    os.symlink(src, dest)


def is_line_in_etc_profile(line):
    """
    /etc/profile 中是否有以 line 开头的行存在

    Parameters:
    -----------
    line: str
        行内容

    Return:
    -------
        bool
    """
    with open("/etc/profile", "r") as f:
        for l in f:
            if l.startswith(line):
                return True
    return False


def append_new_line_to_etc_profile(line):
    """
    在 /etc/profile 中添加一行
    Parameters:
    -----------
    line: str
        要写入的新行

    Returns:
    --------
        None
    """
    with open("/etc/profile", "a") as f:
        f.write(line)
        f.write("\n")


join = os.path.join

readlink = os.readlink

listdir = os.listdir

mkdir = os.mkdir
