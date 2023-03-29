"""

实现自动初始化 dbm-agent 相关的功能
1、创建用户
2、创建用户组
3、创建相应的目录

# 目前给 initilization 的定义是作为代码库中相对独立的部分不参与任何代码重用
"""
# (c) 2019, LeXing Jiang <neeky@live.com 1721900707@qq.com https://www.sqlpy.com/>
# Copyright: (c) 2019, dbm Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import sys
import pwd
import grp
import uuid
import time
import dbma
import shutil
import sqlite3
import logging
import argparse
import subprocess
import contextlib
import configparser
import logging.handlers
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

from . import errors
# exit 1

# 初始化时使用如下日志格式


@contextlib.contextmanager
def sudo(message="sudo"):
    """# sudo 上下文
    提升当前进程的权限到 root 以完成特定的操作，操作完成后再恢复权限
    """
    # 得到当前进程的 euid
    old_euid = os.geteuid()
    # 提升权限到 root
    os.seteuid(0)
    yield message
    # 恢复到普通权限
    os.seteuid(old_euid)


def is_user_exists(user_name: str) -> bool:
    """
    检查操作系统上面是否存在 user_name 变量指定的用户
    """
    try:
        pwd.getpwnam(user_name)
        return True
    except KeyError as err:
        pass
    return False


def is_group_exists(group_name: str) -> bool:
    """
    检查用户组是否存在
    """
    try:
        grp.getgrnam(group_name)
        return True
    except KeyError as err:
        logging.warning(f"user group {group_name} not exits")
        #raise errors.UserNotExistsError()
        return False


def is_root() -> bool:
    """
    检查当前的 euser 是不是 root
    """
    return os.geteuid() == 0


def create_user(user_name: str):
    """
    创建 user_name 给定的用户
    :errors.UserAlreadyExistsError
    :
    """
    if is_user_exists(user_name) == True:
        # 如果用户已经存在就报异常
        raise errors.UserAlreadyExistsError()

    try:
        with sudo(f"create user {user_name} and user group {user_name}"):
            if not is_group_exists(user_name):
                logging.info(f"groupadd {user_name}")
                subprocess.run(f"groupadd {user_name}",
                               shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(
                f"useradd {user_name} -g {user_name} ", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as err:
        logging.error(
            f"an exception been tiggered in create usere stage. {str(err)}")
        logging.error(f"{type(err)}")
        raise errors.ExternalError(f"an exception raise in fun 'create_user' ")


def delete_user(user_name: str):
    """
    删除操作系统级别的用户组
    :errors.UserNotExistsError
    :errors.ExternalError
    """
    if not is_user_exists(user_name):
        raise errors.UserNotExistsError()

    try:
        with sudo(f"delete user {user_name}"):
            subprocess.run(f"userdel {user_name}",
                           shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    except Exception as err:
        raise errors.ExternalError(
            f"an exception raise in fun 'delete_user' raw error {err}")


def get_uid_gid(user_name):
    """
    返回给定用户的 (uid,gid) 组成的元组.
    :errors.UserNotExistsError
    """
    try:
        user = pwd.getpwnam(user_name)
        return user.pw_uid, user.pw_gid
    except KeyError as err:
        # 当给定的用户不存在的话会报 KeyError
        # 把 KeyError 异常转化为 errors.UserNotExistsError
        raise errors.UserNotExistsError()


def render_init_sql(args):
    """
    """
    #tmpl_dir = f"/usr/local/dbm-agent/etc/templates/"
    #tmpl_file = f"init-users.sql.jinja"
    tmpl_dir = os.path.join(args.base_dir, 'etc/templates')
    tmpl_file = f"init-users.sql.jinja"
    env = Environment(loader=FileSystemLoader(searchpath=tmpl_dir))
    tmpl = env.get_template(tmpl_file)
    tmpl.globals = {'initpwd': args.init_pwd}
    init_file = os.path.join(args.base_dir, 'etc/init-users.sql')
    logging.info(f"prepare rende init-sql-file {init_file}")
    with open(init_file, 'w') as cnf:
        sqls = tmpl.render()
        cnf.write(sqls)
    logging.info(f"init-sql-file render complete")


def init_inseption_db(args):
    """
    """
    sql_file = os.path.join(
        args.base_dir, 'etc/templates/auto-inseption-db.sql')
    if not os.path.isfile(sql_file):
        logging.warning(f"init file '{sql_file}' not exists ")
        return

    # 能执行到这里说明 auto-inseption-db.sql 文件是存在的
    with open(sql_file) as f_sql:

        # 读取文件中所有的内容
        sql = f_sql.read()

    # init 阶段 db_file 是不应该存在的，所以这里直接来
    db_file = os.path.join(args.base_dir, 'logs/auto-inseption.db')

    logging.info(f"inseption data saved to '{db_file}' ")
    cnx = None
    try:
        cnx = sqlite3.connect(db_file)
        cursor = cnx.cursor()
        cursor.executescript(sql)
        cnx.commit()

    except Exception as err:
        logging.error(f"init auto inmseption db got error '{err}' ")

    finally:
        if hasattr(cnx, 'close'):
            cnx.close()


def config_monitor_gateway(args):
    """
    """
    # 第一步查询出监控网关的全路径，密码
    cmd = shutil.which("dbm-monitor-gateway")
    password = args.init_pwd

    # 切换到 root 权限
    with dbma.common.sudo("config dbm-monitor-gateway"):

        # 删除已经存在的 systemd 配置文件
        config_file = "/usr/lib/systemd/system/dbm-monitor-gatewayd.service"
        if os.path.isfile(config_file):
            os.remove(config_file)

        # 执行到这里说明 config_file 一定已经不存在了

        # 配置模板
        tmpl_dir = os.path.join(args.base_dir, 'etc/templates')
        tmpl_file = f"dbm-monitor-gatewayd.service.jinja"
        env = Environment(loader=FileSystemLoader(searchpath=tmpl_dir))
        tmpl = env.get_template(tmpl_file)
        tmpl.globals = {'password': password, 'cmd': cmd, 'user': 'monitor'}

        # 渲染模板
        with open(config_file, 'w') as f_config:
            f_config.write(tmpl.render())
        try:
            subprocess.run(['systemctl daemon-reload'], shell=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            subprocess.run(['systemctl enable dbm-monitor-gatewayd'], shell=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            subprocess.run(['systemctl start dbm-monitor-gatewayd'], shell=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception:

            # 不管遇到什么情况都当没有发生
            pass

    logging.info(f"monitor-gateway render complete")


def config_backup_proxy(args):
    """
    """
    # 第一步查询出监控网关的全路径，密码
    cmd = shutil.which("dbm-backup-proxy")

    # 切换到 root 权限
    with dbma.common.sudo("config dbm-backup-proxy"):

        # 删除已经存在的 systemd 配置文件
        config_file = "/usr/lib/systemd/system/dbm-backup-proxyd.service"
        if os.path.isfile(config_file):
            os.remove(config_file)

        # 执行到这里说明 config_file 一定已经不存在了

        # 配置模板
        tmpl_dir = os.path.join(args.base_dir, 'etc/templates')
        tmpl_file = f"dbm-backup-proxyd.service.jinja"
        env = Environment(loader=FileSystemLoader(searchpath=tmpl_dir))
        tmpl = env.get_template(tmpl_file)
        tmpl.globals = {'cmd': cmd}

        # 渲染模板
        with open(config_file, 'w') as f_config:
            f_config.write(tmpl.render())
        try:
            subprocess.run(['systemctl daemon-reload'], shell=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            subprocess.run(['systemctl enable dbm-monitor-gatewayd'], shell=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            subprocess.run(['systemctl start dbm-monitor-gatewayd'], shell=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception:

            # 不管遇到什么情况都当没有发生
            pass

    logging.info(f"monitor-gateway render complete")


def init(args):
    """
    完成所有 dbm-agent 初始化的逻辑
    1、创建用户
    2、创建工作目录 (/usr/local/dbm-agent)
    3、创建配置文件 (/usr/local/dbm-agent/etc/dbma.cnf)
    """
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s", level=logging.DEBUG)

    # 检查用户是不是 root 不是的话就直接退出
    if not is_root():
        logging.error(
            "mast use root user to execute this program. sudo su; dbam-agent init ")
        sys.exit(1)
    # 检查用户 dbma 用户是否存在，如果不存在就创建它
    if not is_user_exists(args.user_name):
        logging.info(
            f" user '{args.user_name}' not exists going to create it ")
        create_user(args.user_name)

    # 检查工作目录是否存在，不存在就创建它 /usr/local/dbm-agent/
    if not os.path.isdir(args.base_dir):
        logging.info(f"create dir {args.base_dir}")
        os.mkdir(args.base_dir)
        os.mkdir(os.path.join(args.base_dir, 'etc'))
        os.mkdir(os.path.join(args.base_dir, 'pkg'))
        os.mkdir(os.path.join(args.base_dir, 'logs'))

    # 增加默认配置文件
    cnf = os.path.join(args.base_dir, 'etc/dbma.cnf')
    logging.info(f"create config file '{cnf}' ")
    parser = configparser.ConfigParser(
        allow_no_value=True, inline_comment_prefixes='#')
    parser['dbma'] = {k: v for k, v in args.__dict__.items() if k != 'action'}
    parser['dbma'].update({'host_uuid': str(uuid.uuid4())})
    with open(cnf, 'w') as cnf:
        parser.write(cnf)

    # 复制 MySQL 配置文件模板
    pkg_dir = os.path.join(os.path.dirname(dbma.__file__), 'static/cnfs')
    shutil.copytree(pkg_dir, os.path.join(args.base_dir, 'etc/templates'))

    #
    render_init_sql(args)
    init_inseption_db(args)
    config_monitor_gateway(args)
    config_backup_proxy(args)

    # 修改 /usr/local/dbm-agent 目录的权限
    if is_user_exists(args.user_name):
        subprocess.run(
            ["chown", "-R", f"{args.user_name}:{args.user_name}", args.base_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #subprocess.run(["chmod","-R",f"600",os.path.join(args.base_dir,'etc') ])

    logging.info("init complete")


def upgrade(args):
    """
    升级 dbm-agent 
    """
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s", level=logging.DEBUG)
    logging.info("going to upgrade dbm-agent")
    pkg_dir = os.path.join(os.path.dirname(dbma.__file__), 'static/cnfs')
    # 备份旧目录
    logging.info("backup etc/templates")
    now = datetime.now()
    shutil.move(os.path.join(args.base_dir, 'etc/templates'),
                os.path.join(args.base_dir, f'etc/templates-backup-{now.isoformat()}'))
    logging.info(f"create new etc/templates")
    shutil.copytree(pkg_dir, os.path.join(args.base_dir, 'etc/templates'))

    # 渲染创建用户的文件
    render_init_sql(args)
    config_monitor_gateway(args)
    config_backup_proxy(args)
    if is_user_exists(args.user_name):
        subprocess.run(
            ["chown", "-R", f"{args.user_name}:{args.user_name}", args.base_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info("upgrade complete")


def uninit(args):
    """
    重置 dbm-agent
    1、检查 dbm-agent 是否在运行、如果是就退出 uninit 操作
    """
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s", level=logging.DEBUG)

    # 检查 dbm-agent 是否已经初始化
    logging.info("checking is dbm-agent has been inited.")
    cnfpath = '/usr/local/dbm-agent/etc/dbma.cnf'
    if not os.path.isdir('/usr/local/dbm-agent') or not os.path.isfile(cnfpath):
        logging.error(
            f"your dbm-agent has not been inited,so unnecessary to uninit it.")
        return
        #raise errors.DBMANotInitedError()

    # 获取 pid 文件保存的路径

    logging.info("checking dbm-agent is runing or not.")
    config = configparser.ConfigParser()
    config.read(cnfpath)
    pid = config['dbma']['pid']

    if os.path.isfile(pid):
        # 如果 pid 文件存在说明 dbm-agent 还在运行中
        # 这个时候不能对它进行 uninit 要先 stop
        logging.error("dbm-agent is runing please stop it 'dbm-agent stop' ")
        return
        #raise errors.DBMAIsRuningError()

    # 可以执行到这里，说明 dbm-agent 已经 init 过，并且已经关闭服务
    logging.info("going to uninit dbm-agent")
    # 第一步：删除用户
    user_name = config['dbma']['user_name']
    delete_user(user_name)

    # 第二步：删除 /usr/local/dbm-agent 目录
    shutil.rmtree('/usr/local/dbm-agent')

    logging.info("uninit compelted goodbye ...")
