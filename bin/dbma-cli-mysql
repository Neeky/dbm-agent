#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""
实例单实例架构下的 MySQL 安装与卸载
"""

import time
import logging
import argparse
from pathlib import Path
from dbma.components.mysql.install import default_pkg
from dbma.components.mysql.install import uninstall_mysql
from dbma.components.mysql.source import install_mysql_source
from dbma.components.mysql.replica import install_mysql_replica
from dbma.components.mysql.commons import make_mysql_writable


def parser_cmd_args():
    """
    实现命令行参数的处理
    """
    parser = argparse.ArgumentParser(
        __name__, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--port", type=int, default=3306, help="instance port")
    parser.add_argument(
        "--pkg-name",
        type=str,
        default=default_pkg.name,
        help="mysql install package name ",
    )
    parser.add_argument(
        "--ibps",
        type=str,
        default="128M",
        help="innodb-buffer-pool-size  et: 128M , 512M, 1G, 2G",
    )
    parser.add_argument(
        "--source",
        type=str,
        default="",
        help="mysql source instance. et: '127.0.0.1:3306' ",
    )
    parser.add_argument(
        "action",
        type=str,
        choices=["master", "slave", "source", "replica", "uninstall"],
    )
    args = parser.parse_args()
    return args


def main():
    #
    args = parser_cmd_args()
    pkg = Path("/usr/local/dbm-agent/pkgs/") / args.pkg_name
    port = args.port
    innodb_buffer_pool_size = args.ibps
    source = args.source
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s %(levelname)s] - [%(threadName)s] - [%(pathname)s %(lineno)d line]  ~  %(message)s",
    )

    if args.action in ("master", "source"):
        # 安装
        install_mysql_source(
            port=port, pkg=pkg, innodb_buffer_pool_size=innodb_buffer_pool_size
        )
    elif args.action in ("slave", "replica"):
        if source == "":
            logging.error(
                "--source is missing , can't find master|source mysql instance ."
            )
            return

        if ":" not in source:
            logging.error("format error --source shuild be ip:port format. ")
            return

        # 解析出 master 实例的地址
        source_ip, source_port = source.split(":")
        source_port = int(source_port)

        # 配置 replica 实例
        install_mysql_replica(
            port, pkg, innodb_buffer_pool_size, source_ip, source_port
        )

    elif args.action == "uninstall":
        uninstall_mysql(args.port)


if __name__ == "__main__":
    main()
