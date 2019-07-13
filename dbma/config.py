"""
针对参数进行处理
1、命令行参数优先于配置文件
2、支持持久化参数，持久化参数优先与配置文件
"""
import os
import sys
import json
import uuid
import argparse
import configparser


__version = '0.0.0.6'

version = lambda : f'dbm-agent-{__version}'

__ALL__ = ['get_config_from_cmd','get_config_from_file']

def get_config_from_cmd():
    parser = argparse.ArgumentParser(version())
    parser.add_argument('--basedir',default='/usr/local/dbm-agent/',help='dbm-agent work dir')
    parser.add_argument('--config-file',default='etc/dbma.cnf',help='dbm-agent config file path')
    parser.add_argument('--log-file',default='logs/dbma.log',help='dbm-agent log file')
    parser.add_argument('--dbmc-site',default='https://192.168.100.100',help='database manage')
    parser.add_argument('--user',default='dbma',help='used for execute dbm-agent')
    parser.add_argument('action',default='start',choices=('start','stop','init'),help='actions')
    args = parser.parse_args()
    return args

def get_config_from_file(config_file='/usr/local/dbm-agent/etc/dbma.cnf'):
    parser = configparser.ConfigParser()
    parser.read(config_file)
    return parser



