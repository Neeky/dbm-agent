# -*- coding: utf8 -*-

"""
实现文件系统的相关操作
"""

import os
import tarfile
from pathlib import Path


def is_file_exists(file_path: Path = None):
    """
    判断文件是否存在

    Parameters:
    -----------
    file_path: Path
        文件|目录 的路径

    Return:
    --------
    bool

    Exceptions:
    -----------
    ValueError
        file_path 为 None 时抛出
    TypeError
        file_path 的类型不为 str | Path 时抛出
    """
    if file_path is None:
        raise ValueError("file_path is None , not a valid value .")

    if type(file_path) not in (str, Path):
        raise TypeError("file_path must be a str, or an Path object .")

    # 如果是 str 的话要传成 Path 对象
    if isinstance(file_path, str):
        file_path = Path(file_path)

    return file_path.exists()


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


def get_file_size(file_path: Path):
    """返回给定文件的大小(字节)

    Parameters:
    -----------
    file_path: Path
        文件路径
    """
    # 如果参数是 str 给它转换成 Path
    if isinstance(file_path, str):
        file_path = Path(file_path)

    res = os.lstat(file_path)
    return res.st_size


def is_file_greater_then(file_path: Path = None, size: int = None):
    """
    检查 file_path 对应文件大小是不是大于 size, 如果是返回 True, 不是返回 False。

    Parameters:
    -----------
    file_path: Path
        文件路径

    size: int
        大小

    Return:
    -------
    bool
    """
    return get_file_size(file_path) > size


def truncate_or_delete_file(file_path: Path = None, chunk_size: int = 16 * 1024 * 1024):
    """
    如果 file_path 的大小大于 chunk_size 就截断 chunk_size 大小的段，不然就删除文件

    Parameters:
    -----------
    file_path: Path
        要执行删除|截断的文件

    chunk_size: int
        单次截断的大小

    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    # 如果已经不足 chunk_size 大，就删除掉；然后就 truncate 指定大小
    file_size = get_file_size(file_path)
    if file_size <= chunk_size:
        os.remove(file_path)
        return 0

    chunk = file_size - chunk_size
    os.truncate(file_path, chunk)
    return chunk


join = os.path.join

readlink = os.readlink

listdir = os.listdir

mkdir = os.mkdir
