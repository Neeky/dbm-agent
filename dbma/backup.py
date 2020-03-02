"""
实现 mysqldump 、mysqlbackup 、extrabackup 的备份

1、完成对 mysqldump ，mysqlbackup、extrabackup 这三个主流工具的封装
2、以给定实例作为输入，找出所有可用的备份工具
3、备份计划
"""

# (c) 2019, LeXing Jiang <neeky@live.com 1721900707@qq.com https://www.sqlpy.com/>
# Copyright: (c) 2019, dbm Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import re
import psutil
import shutil
import logging
import subprocess
from datetime import datetime
from configparser import ConfigParser


from mysql import connector


from . import messages
from . import errors
from . import checkings
from . import common
from .dbmacnf import cnf


logger = logging.getLogger('dbm-agent').getChild(__name__)


class BaseBackup(object):
    """
    实现整个备份流程的各种功能
    """
    args = []
    logger = logging.getLogger("BaseBackup")

    # subprocess.run 时使用
    stdout = subprocess.DEVNULL
    stderr = subprocess.DEVNULL

    def __init__(self, host="127.0.0.1", port=3306, user="mysqldumper", password=None):
        """
        """
        logger = self.logger.getChild("__init__")

        logger.debug(f"prepare backup mysqld{port}")
        self.host = host
        self.port = port
        self.user = user
        self.args = self.args.copy()
        self.now = datetime.now()

        if password is None:

            # 如果没有给定用户名和密码，那么不直接用默认密码
            self.password = cnf.init_pwd
        else:
            self.password = password

    def pre_checks(self):
        """
        在备份之后要执行的验证
        """
        logger = self.logger.getChild("pre_checks")

        # 1、给定的用户能成功连接是，能否备份的一个前提条件
        cnx = None
        try:

            # 创建连接
            cnx = connector.connect(
                host=self.host, port=self.port, user=self.user, password=self.password)
            cursor = cnx.cursor()

            # 可以成功执行到这里就认为通过检测
            cursor.execute("select @@port")
        except Exception as err:

            #
            logger.error(
                f"get error on connecto to host={self.host} port={self.port} user={self.user} password={self.password}")
            raise errors.MySQLIsNotRunningError(str(err))
        finally:
            if hasattr(cnx, 'close'):
                cnx.close()

    def clear(self):
        """
        定义备份完成之后的一些清理工作
        只保留两个备份集
        """
        logger = self.logger.getChild("clear")
        logger.info("start")

        # 取得所有的备份集目录
        backup_base_dir = f"/backup/mysql/backup/{self.port}"
        dir_pattern = re.compile("[0-9]{4}-[0-9]{1,2}")
        dirs = [os.path.join(backup_base_dir, item) for item in os.listdir(
            backup_base_dir) if os.path.isdir(item) and dir_pattern.match(item)]

        # 构建创建时间与目录的元组
        create_time_dirs = [(os.stat(item).st_ctime, item) for item in dirs]

        if len(dirs) >= 3:

            # 如果备份集目录超过三个、找到最老的那个
            _, dir = min(create_time_dirs)
            logger.info(f"prepare remove {dir}")
            shutil.rmtree(dir)
            logger.info(f"done remove {dir}")

        logger.info("complete")

    def save_binlog_position(self):
        """
        保存 binlog 文件的位点信息到 backup-sets/binlog-position.log
        """
        logger = self.logger.getChild("save_binlog_position")
        cnx = None
        try:

            # 文件位置
            backup_log = os.path.join(self.backup_sets, "binlog-position.log")
            now = datetime.now()

            # 位点信息
            cnx = connector.connect(
                host=self.host, port=self.port, user=self.user, password=self.password)
            cursor = cnx.cursor()
            cursor.execute("show master status ;")
            file_name, position, *_ = cursor.fetchone()

            # 保存到文件
            with open(backup_log, 'a') as f:
                f.write(f"{now.isoformat()}    {file_name}    {position} \n")
        except Exception as err:
            logger.error(
                f"exception occur during save_binlog_position {str(err)}")
        finally:
            if hasattr(cnx, 'close'):
                cnx.close()

    @property
    def backup_sets(self):
        """
        返回备份集的目录
        类似于: /backup/mysql/backup/3306/2020-4
        """
        logger = self.logger.getChild("backup_sets")
        year, week, *_ = self.now.isocalendar()
        sts = os.path.join(
            f"/backup/mysql/backup/{self.port}/", f"{year}-{week}")

        logger.debug(f"backup-sets = {sts}")
        return sts

    def backup(self):
        """
        执行备份
        """
        logger = self.logger.getChild("backup")

        # 如果前置检查都过不了，那么就不用备份了
        try:
            self.pre_checks()
        except errors.Error as err:
            logger.error(f"backup opration fail because : {err}")
            return None

        # 如果可以执行到这里，说明基本可以备份了(无法排除权限问题)
        # 完成 args 参数的配置
        logger.info("prepare all setup function")
        self.setup()

        # 打印一下自动化配置下的参数
        logger.info(f"args like this {self.args}")

        # 创建备份集目录
        sts = self.backup_sets
        if not os.path.isdir(sts):
            logger.warn(
                f"backupset dir is not exists we well create it. {sts}")
            # os.mkdir(sts)
            os.makedirs(sts)

        # 保存一下 binlog 的位点信息(方便在做时点还原的时候大致知道从哪个文件开始)
        self.save_binlog_position()

        # 在子进程中备份数据库
        try:
            logger.info("prepare execute mysqlbackup commond")
            subprocess.run(
                self.args, check=True, stderr=self.stderr, stdout=self.stdout)
            # 备份完成之后改一下文件的权限
            # 本来是要用 mysql{self.port} 这个用户备份数据库的，但是遇到 linux 上的一个错误目前还没有解决！！！
            common.recursive_change_owner(sts, f"mysql{self.port}", "mysql")

            logger.info("backup complete")

        except subprocess.CalledProcessError as err:
            logger.error(str(err))
        except subprocess.TimeoutExpired as err:
            logger.error(str(err))
        finally:

            # 资源回收
            if hasattr(self.stdout, 'closed') and self.stdout.closed == False:
                self.stdout.close()
            if hasattr(self.stderr, 'closed') and self.stderr.closed == False:
                self.stderr.close()

            # 临时文件清理
            self.clear()


class MySQLDumpMixin(object):
    """
    完成 mysqldump 相关的基本操作、如查询出 mysqldump 命令在哪里这样的
    """
    logger = logger.getChild("MySQLDumpMixin")
    # args 将来要用于 subprocess.run 函数
    args = []

    defautls = {
        'triggers': '',
        'routines': '',
        'events': '',
        'compress': '',
        'all-databases': '',
        'default-character-set': 'binary',
        'delete-master-logs': 'OFF',
        # 'flush-logs': '',
        'flush-privileges': '',
        'master-data': 2,
        'single-transaction': 'ON',
        'max-allowed-packet': '128M',
        'dump-date': '',
    }

    def get_mysqldump_cmd(self):
        """
        查询出 mysqldump 的绝对路径
        """
        logger = self.logger.getChild("get_mysqldump_cmd")

        cnx = None
        try:
            cnx = connector.connect(
                host=self.host, port=self.port, user=self.user, password=self.password)
            cursor = cnx.cursor()
            cursor.execute("select @@basedir;")

            # 查询出 basedir 是多少
            basedir, *_ = cursor.fetchone()
            cmd = os.path.join(basedir, 'bin/mysqldump')

            logger.info(messages.USING_XX_AS_BACKUP_TOOL.format(cmd))
            return cmd
        except Exception as err:
            logger.warn(str(err))

        finally:
            if hasattr(cnx, 'close'):
                cnx.close()

    def get_defaults(self, kwargs=None):
        """
        返回在 MySQLDumpMixin 这个级别就可以确定的参数
        """
        logger = self.logger.getChild("get_defaults")

        # 复制默认值
        if kwargs is None:
            kwargs = {}

        options = self.defautls.copy()
        options.update({'user': self.user, 'password': self.password,
                        'host': self.host, 'port': self.port})
        options.update(kwargs)
        logger.debug(f"options like this {options}")

        return options

    def setup(self):
        """
        完成 mysqlump 的基本参数
        """
        logger = self.logger.getChild("setup")

        cmd = self.get_mysqldump_cmd()
        logger.info(f"using {cmd} to backup")
        self.args = [cmd, ]
        for k, v in self.get_defaults().items():
            if v != '':
                self.args.append(f'--{k}={v}')
            else:
                self.args.append(f'--{k}')
        # 设置stdout 和 stderr
        self.stdout = subprocess.DEVNULL
        self.stderr = subprocess.DEVNULL


class MySQLBackupMixin(object):
    """
    完成 mysqlbackup 相关的基本操作
    """
    logger = logger.getChild("MySQLBackupMixin")
    args = []
    defaults = {
        'on-disk-full': 'abort_and_remove',
        'compress': '',
        'skip-binlog': '',
        'skip-relaylog': '',
        'progress-interval': 1,
        'process-threads': 1,
        'read-threads': 1,
        'write-threads': 1,
        'limit-memory': 128,
    }

    def get_mysqlbackup_cmd(self):
        """
        返回对应版本的 mysqldump 命令
        """
        logger = self.logger.getChild("get_mysqlbackup_cmd")
        cnx = None
        try:

            # 查询出 mysql 的版本号
            cnx = connector.connect(
                host=self.host, port=self.port, user=self.user, password=self.password)
            cursor = cnx.cursor()
            cursor.execute("select @@version;")
            version, *_ = cursor.fetchone()

            # 拼接出对应版本的 meb 工具
            mysqlbackup = f"/usr/local/mysql-commercial-backup-{version}-linux-glibc2.12-x86_64/bin/mysqlbackup"
            if os.path.isfile(mysqlbackup):

                # 如果存在就返回
                return mysqlbackup

            mysqlbackup = f"/usr/local/meb/bin/mysqlbackup"
            if os.path.isfile(mysqlbackup):

                # 在 /usr/local/meb/bin 下可以找到能用的也行
                return mysqlbackup

            # 如果执行到这里，说明以上两个地方都找不到就返回 None
            return None

        except Exception as err:
            logger.error(str(err))
            return None
        finally:
            if hasattr(cnx, 'close'):
                cnx.close()

    def get_defaults(self, kwargs=None):
        """
        返回 args 
        """
        if kwargs is None:
            kwargs = {}

        options = self.defaults.copy()
        options.update(kwargs)
        options.update({'user': self.user, 'password': self.password,
                        'host': self.host, 'port': self.port})

        # 备份进度
        sts = self.backup_sets
        progress_file = os.path.join(f"file:{sts}", "mysqlbackup-progress.log")
        options.update({'show-progress': progress_file})
        logger.debug(f"options like this {options}")

        # 读并发
        cpu = psutil.cpu_count()
        read_threads = int(cpu * 0.1) + 1
        process_threads = int(cpu * 0.2) + 2
        write_threads = int(cpu * 0.1) + 1
        options.update({
            'read-threads': read_threads,
            'write-threads': write_threads,
            'process-threads': process_threads,
        })

        # 内存占用情况
        available = psutil.virtual_memory().available / 1024 / 1024
        limit_memory = 128

        if available >= 1024:
            limit_memory = 256
        elif available >= 2048:
            limit_memory = 512
        elif available >= 3072:
            limit_memory = 1024
        elif available >= 4096:   # 4G
            limit_memory = 1152
        elif available >= 6144:   # 8G
            limit_memory = 2048
        elif available >= 10240:  # 10G
            limit_memory = 3072
        elif available >= 12288:  # 12G
            limit_memory = 4096
        elif available >= 16384:  # 16G
            limit_memory = 6144
        else:
            limit_memory = 10240

        options.update({'limit-memory': limit_memory})

        return options

    def setup(self):
        """
        """
        logger = self.logger.getChild("setup")

        # 解析出命令
        cmd = self.get_mysqlbackup_cmd()
        logger.info(f"using {cmd} to backup")
        self.args = [cmd, ]

        # 创建临时目录
        sts = self.backup_sets
        backup_dir = os.path.join(
            sts, f"{self.now.isoformat()[:19]}-temp")

        if not os.path.isdir(backup_dir):

            # 如果临时目录还没有那么就创建出来
            os.makedirs(backup_dir)

        # 把 self.stderr 设置上
        # backup 函数会对这个做 close
        stderr = os.path.join(sts, f"{self.now.isoformat()}.log")
        self.stderr = open(stderr, 'w')

        # 把属性添加到 self 方便后面使用
        self.backup_dir = backup_dir
        logger.info(f"set backup-dir to {backup_dir}")

        #
        for k, v in self.get_defaults(kwargs={'backup-dir': backup_dir}).items():
            if v != '':
                self.args.append(f'--{k}={v}')
            else:
                self.args.append(f'--{k}')

        # 添加 backup-to-image
        self.args.append('backup-to-image')


class XtraBackupMixin(object):
    """
    """
    logger = logger.getChild("XtraBackupMixin")
    args = []
    defaults = {
        'compress': '',
    }


class MySQLBackupFullBackupMixin(MySQLBackupMixin):
    """
    实现 mysqlbackup 进行全备的相关逻辑
    """
    logger = logger.getChild("MySQLBackupFullBackupMixin")

    def get_defaults(self, kwargs=None):
        """
        """
        logger = self.logger.getChild("get_defaults")

        if kwargs is None:
            kwargs = {}

        # 把 backup-image 加上就可以了
        sts = self.backup_sets
        backup_image = os.path.join(
            sts, f"{self.now.isoformat()}-full-backup.mbi")
        kwargs.update({'backup-image': backup_image})
        #logger.info(f"kwargs = {kwargs}")

        options = MySQLBackupMixin.get_defaults(self, kwargs)

        logger.info(options)
        return options


class MySQLBackupDiffBackupMixin(MySQLBackupMixin):
    """
    """
    logger = logger.getChild("MySQLBackupDiffBackupMixin")

    def get_defaults(self, kwargs=None):
        """
        """
        logger = self.logger.getChild("get_defaults")

        if kwargs is None:
            kwargs = {}

        # 设置 backup-image
        sts = self.backup_sets
        backup_image = os.path.join(
            sts, f"{self.now.isoformat()}-diff-backup.mbi")
        kwargs.update({'backup-image': backup_image})

        # 设置 --increament
        kwargs.update(
            {'incremental': '', 'incremental-base': 'history:last_full_backup'})

        options = MySQLBackupMixin.get_defaults(self, kwargs)

        # logger.info(options)
        return options


class MySQLDumpFullBackupMixin(MySQLDumpMixin):
    """
    """

    logger = logger.getChild("MySQLDumpFullBackupMixin")

    def get_defaults(self, kwargs=None):
        """
        """
        if kwargs is None:
            kwargs = {}

        sts = self.backup_sets
        backup_file = os.path.join(
            sts, f'{self.now.isoformat()}-full-backup.sql')
        kwargs.update({'result-file': backup_file})
        return MySQLDumpMixin.get_defaults(self, kwargs)


class MySQLDumpNoDataMixin(MySQLDumpMixin):
    """
    实现只 dump schema 相关的逻辑
    """
    logger = logger.getChild("MySQLDumpNoDataMixin")

    def get_defaults(self, kwargs=None):
        """
        """
        if kwargs is None:
            kwargs = {}

        options = MySQLDumpMixin.get_defaults(self)
        del options['flush-privileges']
        del options['master-data']
        del options['single-transaction']

        sts = self.backup_sets
        options['result-file'] = os.path.join(sts,
                                              f'{self.now.isoformat()}-only-schema.sql')
        options['no-data'] = ''

        return options


# mysqldump 支持两个备份模式 “全量” “只备份定义(only-schema)”

class MySQLDumpFullBackup(MySQLDumpFullBackupMixin, BaseBackup):
    """
    实现 mysqldump 进行全量备份的所有逻辑
    """
    pass


class MySQLDumpNoDataBackup(MySQLDumpNoDataMixin, BaseBackup):
    """
    实现 mysqldump 只导出 schema 的相关逻辑
    """
    pass


# mysqlbackup 支持两种备份模板 “全量”，“差异”

class MySQLBackupFullBackup(MySQLBackupFullBackupMixin, BaseBackup):
    """
    实现基于 mysqlbackup 的全量备份
    """
    pass


class MySQLBackupDiffBackup(MySQLBackupDiffBackupMixin, BaseBackup):
    """
    实现基于 mysqlbackup 的差异备份逻辑
    """


def usable_backup_tools(host="127.0.0.1", port=3306, user="mysqldump", password="dbma@0352"):
    """
    解析出当前实例下所有可用的备份工具
    """
    lgr = logger.getChild("usable_backup_tools")

    # 连接上实例，用于确认版本号和 basedir
    cnx = None
    tools = []
    try:
        lgr.info(
            f"prepare connect to host={host} port={port} user={user} password={password}")
        cnx = connector.connect(host=host, port=port,
                                user=user, password=password)
        cursor = cnx.cursor()
        cursor.execute("select @@version,@@basedir")
        version, basedir = cursor.fetchone()

        lgr.info(f"version = {version}")
        lgr.info(f"basdir = {basedir}")
        # 查询对应版本的 meb 是否存在
        mysqlbacup = f"/usr/local/mysql-commercial-backup-{version}-linux-glibc2.12-x86_64/bin/mysqlbackup"
        if os.path.isfile(mysqlbacup):
            lgr.info("mysqlbackup exists")

            tools.append("mysqlbackup")

        # 查询 mysqldump 是否存在
        mysqldump = os.path.join(basedir, "bin/mysqldump")
        if os.path.isfile(mysqldump):
            lgr.info("mysqldump exists")
            tools.append("mysqldump")

    except Exception as err:
        lgr.error(f"{str(err)}")
    finally:
        if hasattr(cnx, 'close'):
            cnx.close()

    lgr.info(tools)
    return tools


def get_current_backup_sets(port=3306):
    """查询当前实例应该使用的备份集信息
    """
    year, week, *_ = datetime.now().isocalendar()
    sts = os.path.join(
        f"/backup/mysql/backup/{port}/", f"{year}-{week}")
    return sts


class BackupChecker(object):
    """检查备份是否存在于是否成功
    """
    logger = logger.getChild("BackupChecker")

    def __init__(self, port=3306):
        """
        """
        logger = self.logger.getChild("__init__")
        logger.info("start")

        self.port = port
        # 当前时间的前缀 2020-02-22
        self.todaystr = datetime.now().isoformat()[:10]
        year, week, *_ = datetime.now().isocalendar()
        self.backup_set_dir = os.path.join(
            f"/backup/mysql/backup/{port}/", f"{year}-{week}")

        logger.info("complete")

    @property
    def has_backup_set(self):
        """检查是否有备份集
        """
        logger = self.logger.getChild("has_backup_set")
        logger.info("start")

        # 如果备份集的目录不存在那么就是没有
        if not os.path.exists(self.backup_set_dir):
            logger.info("complete")
            return False
        else:
            logger.info("complete")
            return True

    @property
    def has_mbi_full_backup(self):
        """检查是否有 mysqlbackup 做的全备
        """
        logger = self.logger.getChild("has_mbi_full_backup")
        logger.info("start")

        #
        if self.has_backup_set == False:

            # 备份集都没有就不可能有基于 mysqlbackup 的全备文件
            logger.debug("backup set not exists")
            logger.info("complete")
            return False

        # 执行到这里说明备份集存在于是检查是否有全备文件

        backups = [backup for backup in os.listdir(
            self.backup_set_dir) if backup.endswith("full-backup.mbi")]
        logger.info(f"{backups}")

        if len(backups) == 0:

            # 空列表说明没有全备
            logger.info("complete")
            return False

        # 执行到这里说明 全备文件是存在的，那么就要检查它是否成功了
        * _, lastbackup = backups
        logfile = lastbackup[:26] + '.log'
        log_file_path = os.path.join(self.backup_set_dir, logfile)

        # 如果文件这个时候被删除了，那么就有可能不存在，所以先检查一下
        if not os.path.isfile(log_file_path):
            logger.warning(f"log file '{log_file_path}' not exists")
            logger.info("complete")
            return False

        # 执行到这里说明文件是有的
        log_file_size = os.stat(log_file_path).st_size
        logger.info(f"prepare open {log_file_path}")
        with open(log_file_path) as logfile:

            # 指向最后 100 个字节
            logfile.seek(log_file_size - 100)
            for line in logfile:

                # 能找到成功的标志就说明成功了，不然说说明没有成功
                if 'mysqlbackup completed OK!' in line:
                    logger.info("complete")
                    return True

        logger.info("complete")
        return False

    @property
    def has_mbi_diff_backup(self):
        """检查增量备份是否成功
        """
        logger = self.logger.getChild("has_mbi_diff_backup")
        logger.info("start")

        # 如果备份集都没有那么就认为 diff 备份也没有
        if self.has_backup_set == False:
            logger.warning("backup set dir not exists")
            logger.info("complete")
            return False

        # 执行到这里说明备份集是有的，那么准备找今天有没有 diff 备份,full 也看成是 diff
        backups = [backup for backup in os.listdir(self.backup_set_dir) if backup.startswith(
            self.todaystr) and backup.endswith(".log")]
        if len(backups) == 0:

            #
            logger.warning("cant find any backup file ")
            logger.info("complete")
            return False

        # 执行到这里说明是有日志文件的、那么就看一下最后一个备份日志文件中有没有记录成功
        * _, logfile = backups
        log_file_path = os.path.join(self.backup_set_dir, logfile)
        log_file_size = os.stat(log_file_path).st_size

        with open(log_file_path) as logfile:

            #
            logger.info("")
            logfile.seek(log_file_size - 100)
            for line in logfile:

                # 如果有成功的标示就说明成功了
                if 'mysqlbackup completed OK!' in line:
                    logger.info("complete")
                    return True

        logger.info("complete")
        return False

    @property
    def has_sql_backup(self):
        """检查今天 mysqldump 的备份有没有成功
        """
        logger = self.logger.getChild("has_sql_backup")
        logger.info("start")

        if self.has_backup_set == False:

            logger.warning("backup set not exits")
            logger.info("complete")
            return False

        #
        backups = [backup for backup in os.listdir(
            self.backup_set_dir) if backup.endswith("full-backup.sql")]

        # 检查备份集是否存在
        if len(backups) == 0:

            #
            logger.warning("backup set is empty")
            logger.info("complete")
            return False

        #
        * _, lastbackup = backups
        last_backup_file_path = os.path.join(self.backup_set_dir, lastbackup)
        last_backup_file_size = os.stat(last_backup_file_path).st_size

        with open(last_backup_file_path) as backupfile:
            backupfile.seek(last_backup_file_size - 100)
            for line in backupfile:
                if '-- Dump completed on' in line:

                    #
                    logger.info(
                        f"has available backup '{last_backup_file_path}' ")
                    logger.info("complete")
                    return True

        logger.info("complete")
        return False


def today_has_backup(port=3306):
    """
    检查今天是否已经备份过
    """
    lgr = logger.getChild("today_has_backup")

    today = datetime.now().isoformat()[:10]
    year, week, *_ = datetime.now().isocalendar()
    sts = os.path.join(
        f"/backup/mysql/backup/{port}/", f"{year}-{week}")
    if not os.path.isdir(sts):
        # 如果备份集都没有，那么是一定没有备份的
        lgr.info("backup sets not exists.")
        return False

    # 执行到这里说明有备份集
    backups = []
    for backup in os.listdir(sts):
        if backup.startswith(today):
            backups.append(backup)

    # 如果列表的长度是空的那么今天定是没有备份的
    if len(backups) == 0:

        # 说明今天还没有备份
        lgr.info("backup file not exists")
        return False

    # 执行到这里说明是有备份的，那么就要检查备份是否成功了
    backups = [backup for backup in backups if backup.endswith(
        '.log') or backup.endswith('sql')]
    * _, backup = backups
    # 取得最后的一个备份文件

    lgr.info("validate backup file")
    file_abs_path = os.path.join(sts, backup)
    file_size = os.stat(file_abs_path).st_size
    with open(file_abs_path) as f:
        f.seek(file_size - 100)
        for line in f:
            if "mysqlbackup completed OK!" in line or "-- Dump completed on" in line:
                lgr.info("backup file valid")
                return True

    lgr.info("backup file validate fail we need a new one")
    return False


def has_full_backup(port=3306):
    """检查是否有可用的全备
    """
    lgr = logger.getChild("has_full_backup")
    lgr.info("start")

    # 如果备份集的目录不存在那么一定是没有的
    today = datetime.now().isoformat()[:10]
    year, week, *_ = datetime.now().isocalendar()
    sts = os.path.join(
        f"/backup/mysql/backup/{port}/", f"{year}-{week}")
    if not os.path.isdir(sts):
        # 如果备份集都没有，那么是一定没有备份的
        lgr.info("backup sets not exists.")
        return False

    # 目录已经存在就要检查全备是否成功
    # 使用 mysqldump 的情况
    lgr.debug("prepare checking has *full-backup.sql file or not")
    mysqldumps = [dump for dump in os.listdir(
        sts) if dump.endswith("full-backup.sql")]
    lgr.debug(f"find dump files {mysqldumps}")

    if len(mysqldumps) == 0:
        lgr.debug("full backup not exists")
        return False


def clean_backup_sets(port=3306, sets_count=2):
    """
    清理备份集(第次至多清理一个)
    """
    logger.debug("checking is there has any backup sets can remove")
    backups = []
    backup_base_dir = f"/backup/mysql/bacup/{port}"
    pattern = r"\d{4}-\d{1,2}"
    for sets in os.listdir(backup_base_dir):

        sets_dir = os.path.join(backup_base_dir, sets)
        if os.path.isdir(sets_dir) and re.match(pattern, sets):
            backups.append(os.path.join(backup_base_dir, sets))

    if len(backups) > sets_count:
        logger.info(f"current backup sets {backups}")
        oldest, *_ = backups
        logger.info(f"remove backup set {oldest}")
        os.removedirs(oldest)


def backup_binlog(port=3306):
    """
    """

    pass
