#!/usr/bin/evn python3

# (c) 2019, LeXing Jiang <neeky@live.com 1721900707@qq.com https://www.sqlpy.com/>
# Copyright: (c) 2019, dbm Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import re
import os
import sys
import time
import socket
import random
import shutil
import pathlib
import logging
import threading
import subprocess
from mysql import connector
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

from . import checkings
from .dbmacnf import cnf
from . import errors
from . import common


logger = logging.getLogger('dbm-agent').getChild(__name__)


class MyCnfRender(object):
    """
    实现对 mysql 配置文件模板的渲染工作
    """

    logger = logger.getChild('MyCnfRender')
    dbma = cnf

    def __init__(self, basedir="/usr/local/mysql-8.0.17-linux-glibc2.12-x86_64/",
                 datadir="/database/mysql/data/3306/", binlogdir="/binlog/mysql/binlog/3306/",
                 max_mem=128, cores=1, port=3306, user="mysql3306"
                 ):
        """
        """
        self.max_mem = max_mem
        self.cores = int(cores)
        self.binlogdir = binlogdir
        # basic
        self.user = user
        self.port = port
        self.mysqlx_port = port * 10
        self.admin_port = port * 10 + 2
        self.admin_address = '127.0.0.1'
        self.basedir = basedir
        self.datadir = datadir
        self.socket = f"/tmp/mysql-{port}.sock"
        self.mysqlx_socket = f"/tmp/mysqlx-{self.mysqlx_port}.sock"
        self.pid_file = f"/tmp/mysql-{port}.pid"
        self.server_id = random.randint(1, 4097)
        self.open_files_limit = 102000
        self.max_prepared_stmt_count = 1048576
        self.skip_name_resolve = 1
        self.super_read_only = 'OFF'
        self.sql_require_primary_key = 'OFF'
        self.lower_case_table_names = 1
        self.auto_increment_increment = 1
        self.auto_increment_offset = 1
        self.event_scheduler = 'OFF'
        self.auto_generate_certs = 'ON'
        self.big_tables = 'OFF'
        self.join_buffer_size = '256K'
        self.activate_all_roles_on_login = 'ON'
        self.end_markers_in_json = 'OFF'
        self.tmpdir = '/tmp/'
        self.max_connections = 128
        self.autocommit = 'ON'
        self.sort_buffer_size = '256K'
        self.eq_range_index_dive_limit = 200
        self.character_set_server = 'utf8mb4'
        self.performance_schema = 'ON'

        # table cache
        self.table_open_cache = 4000
        self.table_definition_cache = 2000
        self.table_open_cache_instances = 32

        # net
        self.max_allowed_packet = '1G'
        self.bind_address = '*'
        self.connect_timeout = 10
        self.interactive_timeout = 28800
        self.net_read_timeout = 30
        self.net_retry_count = 10
        self.net_write_timeout = 60
        self.net_buffer_length = '32K'

        # logs
        self.log_output = 'FILE'
        self.log_timestamps = 'system'
        self.general_log = 'OFF'
        self.general_log_file = 'general.log'

        self.log_error = "err.log"

        self.long_query_time = 2
        self.log_queries_not_using_indexes = 'OFF'
        self.log_slow_admin_statements = 'OFF'
        self.log_slow_slave_statements = 'OFF'
        self.slow_query_log = 'ON'
        self.slow_query_log_file = 'slow.log'

        # binlog
        self.log_bin = os.path.join(self.binlogdir, 'mysql-bin')
        self.log_statements_unsafe_for_binlog = 'ON'
        self.binlog_checksum = 'none'
        self.log_bin_trust_function_creators = 'ON'
        self.binlog_direct_non_transactional_updates = 'OFF'
        self.binlog_expire_logs_seconds = 604800
        self.binlog_error_action = 'ABORT_SERVER'
        self.binlog_format = 'ROW'
        self.max_binlog_stmt_cache_size = '1G'
        self.max_binlog_cache_size = '1G'
        self.max_binlog_size = '1G'
        self.binlog_order_commits = 'ON'
        self.binlog_row_image = 'FULL'
        self.binlog_row_metadata = 'MINIMAL'
        self.binlog_rows_query_log_events = 'ON'
        self.sync_binlog = 1
        self.binlog_stmt_cache_size = '32K'
        self.log_slave_updates = 'ON'
        self.binlog_transaction_compression = 'ON'
        self.binlog_group_commit_sync_delay = 0
        self.binlog_group_commit_sync_no_delay_count = 0
        self.binlog_cache_size = '96K'
        self.binlog_transaction_dependency_history_size = 25000
        self.binlog_transaction_dependency_tracking = 'WRITESET'

        # replication
        self.rpl_semi_sync_master_enabled = 1
        self.master_info_repository = 'table'
        self.sync_master_info = 10000
        self.rpl_semi_sync_master_timeout = 1000
        self.relay_log_info_repository = 'table'
        self.skip_slave_start = 'OFF'
        self.slave_parallel_type = 'logical_clock'
        self.slave_parallel_workers = 2
        self.slave_max_allowed_packet = '1G'
        self.slave_load_tmpdir = '/tmp/'
        self.relay_log = 'relay'
        self.sync_relay_log = 10000
        self.sync_relay_log_info = 10000
        self.rpl_semi_sync_slave_enabled = 1
        self.slave_preserve_commit_order = 'ON'
        self.rpl_semi_sync_master_wait_point = "AFTER_SYNC"
        self.rpl_semi_sync_master_wait_no_slave = "ON"
        self.rpl_semi_sync_master_wait_for_slave_count = 1

        # gtid
        self.binlog_gtid_simple_recovery = 'ON'
        self.enforce_gtid_consistency = 'ON'
        self.gtid_executed_compression_period = 1000
        self.gtid_mode = 'ON'

        # engines
        self.default_storage_engine = 'innodb'
        self.default_tmp_storage_engine = 'innodb'
        self.internal_tmp_mem_storage_engine = 'TempTable'

        # innodb
        self.innodb_data_home_dir = './'
        self.innodb_data_file_path = 'ibdata1:64M:autoextend'
        self.innodb_page_size = '16K'
        self.innodb_default_row_format = 'dynamic'
        self.innodb_log_group_home_dir = './'
        self.innodb_log_files_in_group = 8
        self.innodb_log_file_size = '128M'
        self.innodb_log_buffer_size = '128M'
        self.innodb_redo_log_encrypt = 'OFF'
        self.innodb_online_alter_log_max_size = '256M'
        self.innodb_undo_directory = './'
        self.innodb_undo_log_encrypt = 'OFF'
        self.innodb_undo_log_truncate = 'ON'
        self.innodb_max_undo_log_size = '1G'
        self.innodb_rollback_on_timeout = 'OFF'
        self.innodb_rollback_segments = 128
        self.innodb_log_checksums = 'ON'
        self.innodb_checksum_algorithm = 'crc32'
        self.innodb_log_compressed_pages = 'ON'
        self.innodb_doublewrite = 'ON'
        self.innodb_commit_concurrency = 0
        self.innodb_read_only = 'OFF'
        self.innodb_dedicated_server = 'OFF'
        self.innodb_buffer_pool_chunk_size = '128M'
        self.innodb_buffer_pool_size = '128M'
        self.innodb_buffer_pool_instances = 1
        self.innodb_old_blocks_pct = 37
        self.innodb_old_blocks_time = 1000
        self.innodb_random_read_ahead = 'OFF'
        self.innodb_read_ahead_threshold = 56
        self.innodb_max_dirty_pages_pct_lwm = 20
        self.innodb_max_dirty_pages_pct = 90
        self.innodb_flush_neighbors = 0
        self.innodb_lru_scan_depth = 1024
        self.innodb_adaptive_flushing = 'ON'
        self.innodb_adaptive_flushing_lwm = 10
        self.innodb_flushing_avg_loops = 30
        self.innodb_buffer_pool_dump_pct = 50
        self.innodb_buffer_pool_dump_at_shutdown = 'ON'
        self.innodb_buffer_pool_load_at_startup = 'ON'
        self.innodb_buffer_pool_filename = 'ib_buffer_pool'
        self.innodb_stats_persistent = 'ON'
        self.innodb_stats_on_metadata = 'ON'
        self.innodb_stats_method = 'nulls_equal'
        self.innodb_stats_auto_recalc = 'ON'
        self.innodb_stats_include_delete_marked = 'ON'
        self.innodb_stats_persistent_sample_pages = 20
        self.innodb_stats_transient_sample_pages = 8
        self.innodb_status_output = 'OFF'
        self.innodb_status_output_locks = 'OFF'
        self.innodb_buffer_pool_dump_now = 'OFF'
        self.innodb_buffer_pool_load_abort = 'OFF'
        self.innodb_buffer_pool_load_now = 'OFF'
        self.innodb_thread_concurrency = 0
        self.innodb_concurrency_tickets = 5000
        self.innodb_thread_sleep_delay = 15000
        self.innodb_adaptive_max_sleep_delay = 150000
        self.innodb_read_io_threads = 4
        self.innodb_write_io_threads = 4
        self.innodb_use_native_aio = 'ON'
        self.innodb_flush_sync = 'OFF'
        self.innodb_io_capacity = 4000
        self.innodb_io_capacity_max = 20000
        self.innodb_spin_wait_delay = 6
        self.innodb_purge_threads = 4
        self.innodb_purge_batch_size = 300
        self.innodb_purge_rseg_truncate_frequency = 128
        self.innodb_deadlock_detect = 'ON'
        self.innodb_autoinc_lock_mode = 2
        self.innodb_print_all_deadlocks = 'ON'
        self.innodb_lock_wait_timeout = 50
        self.innodb_table_locks = 'ON'
        self.innodb_sync_array_size = 1
        self.innodb_sync_spin_loops = 30
        self.innodb_print_ddl_logs = 'OFF'
        self.innodb_replication_delay = 0
        self.innodb_cmp_per_index_enabled = 'OFF'
        self.innodb_disable_sort_file_cache = 'OFF'
        self.innodb_numa_interleave = 'OFF'
        self.innodb_strict_mode = 'ON'
        self.innodb_sort_buffer_size = '1M'
        self.innodb_fast_shutdown = 1
        self.innodb_force_load_corrupted = 'OFF'
        self.innodb_force_recovery = 0
        self.innodb_temp_tablespaces_dir = './#innodb_temp/'
        self.innodb_tmpdir = './'
        self.innodb_temp_data_file_path = 'ibtmp1:64M:autoextend'
        self.innodb_page_cleaners = 4
        self.innodb_adaptive_hash_index = 'ON'
        self.innodb_adaptive_hash_index_parts = 8
        self.innodb_flush_log_at_timeout = 1
        self.innodb_flush_log_at_trx_commit = 1
        self.innodb_flush_method = 'O_DIRECT'
        self.innodb_fsync_threshold = 0
        self.innodb_change_buffer_max_size = 25
        self.innodb_change_buffering = 'all'
        self.innodb_fill_factor = 90
        self.innodb_file_per_table = 'ON'
        self.innodb_autoextend_increment = 64
        self.innodb_open_files = 100000

        # mgr
        self.is_mgr = False
        self.group_replication_single_primary_mode = "ON"
        self.group_replication_group_name = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        self.group_replication_start_on_boot = "OFF"
        self.group_replication_bootstrap_group = "OFF"
        self.group_replication_local_address = None
        self.group_replication_group_seeds = None
        self.group_replication_recovery_use_ssl = 'ON'
        self.group_replication_ssl_mode = 'REQUIRED'
        self.group_replication_consistency = 'EVENTUAL'
        self.group_replication_poll_spin_loops = 0
        self.group_replication_compression_threshold = 1000000
        self.group_replication_communication_max_message_size = '128M'
        self.group_replication_message_cache_size = '1G'
        self.group_replication_flow_control_applier_threshold = 25000
        self.group_replication_flow_control_certifier_threshold = 25000
        self.group_replication_flow_control_hold_percent = 10
        self.group_replication_flow_control_mode = 'QUOTA'
        self.group_replication_flow_control_period = 1
        self.group_replication_flow_control_release_percent = 50

    def _config_cpus(self):
        """
        根据 cpu 核心数量重新配置配置文件中相关的参数
        """
        logger = self.logger.getChild('_config_cpus')

        logger.debug("start config cpu related variables")

        if self.cores <= 8:
            pass
        elif self.cores <= 16:
            self.innodb_read_io_threads = 6
        elif self.cores <= 24:
            self.innodb_write_io_threads = 6
        elif self.cores <= 40:
            self.innodb_read_io_threads = 8
            self.innodb_purge_threads = 6
        elif self.cores <= 80:
            self.innodb_read_io_threads = 8
            self.innodb_write_io_threads = 8
            self.innodb_page_cleaners = 6
        else:
            self.innodb_read_io_threads = 8
            self.innodb_write_io_threads = 8
            self.innodb_purge_threads = 8
            self.innodb_page_cleaners = 8

    def _config_mems(self):
        """
        根据 mem 核心数量重新配置配置文件中相关的参数
        """

        logger = self.logger.getChild('_config_mems')

        chunk = 1
        if self.max_mem <= 512:

            # 如果给定的内存小于 512M 那直接只分配一个 chunk 就行
            chunk = 1
        elif self.max_mem <= 1024:

            # 如果给定的内存在 (513,1024] 之间分配两个 chunk
            chunk = 2
        elif self.max_mem <= 4096:

            # 给定的内存大于 1G 但是小于 4G 分配 50%
            chunk = int((self.max_mem // 128) * 0.5)
        elif self.max_mem <= 1024 * 8:

            # 如果给定的内存在区间 （4G,8G] 内就分配 55%
            chunk = int((self.max_mem // 128) * 0.55)
        elif self.max_mem <= 1024 * 16:

            # 如果给定的内存在区间 （8G,16G] 内就分配 60%
            chunk = int((self.max_mem // 128) * 0.60)
        elif self.max_mem <= 1024 * 32:

            # 如果给定的内存在区间 （16G,32G] 内就分配 65%
            chunk = int((self.max_mem // 128) * 0.65)
        elif self.max_mem <= 1024 * 64:

            # 如果给定的内存在区间 （32G,64G] 内就分配 70%
            chunk = int((self.max_mem // 128) * 0.70)
        elif self.max_mem <= 1024 * 128:

            # 如果给定的内存在区间 （64G,128G] 内就分配 75%
            chunk = int((self.max_mem // 128) * 0.75)
        elif self.max_mem <= 1024 * 256:

            # 如果给定的内存在区间 （128G,256G] 内就分配 80%
            chunk = int((self.max_mem // 128) * 0.80)
        else:
            # 如果给定的内存在区间 （256G,++G] 内就分配 85%
            chunk = int((self.max_mem // 128) * 0.85)

        # 根据 chunk 的数量分配 innodb_buffer_pool_size
        if chunk % 4 == 0:

            # 可以被 4 整除就用 G 做单位
            self.innodb_buffer_pool_size = f"{int(chunk / 8)}G"
        else:
            # 不可以被 4 整除就用 M 做单位
            self.innodb_buffer_pool_size = f"{int(chunk * 128)}M"
        logger.debug(
            f"change innodb_buffer_pool_size to {self.innodb_buffer_pool_size}")

        # 根据 chunk 的数量确定 innodb-buffer-pool-instances 的数量
        instances = chunk // 8 if chunk >= 8 else 1  # 至少每两 G 一个 instance

        # 最多也就分配 32 个实例
        if instances >= 32:
            instances = 32
        self.innodb_buffer_pool_instances = instances
        logger.debug(
            f"change innodb_buffer_pool_instances to {self.innodb_buffer_pool_instances}")

        # 只有在 innodb_buffer_pool_size > 2G 的情况下才有必要开启 performance_schema
        self.performance_schema = 'ON' if chunk >= 16 else 'OFF'
        logger.debug(f"change performance_schema to {self.performance_schema}")

        # dbm-agent 默认会分配 8 个 redo 文件
        if chunk <= 8:

            # buffer_pool <= 1G
            self.innodb_log_file_size = '64M'
            self.innodb_log_buffer_size = '64M'
        elif chunk <= 16:

            # 1G < buffer_pool <= 2G
            self.innodb_log_file_size = '128M'
            self.innodb_log_buffer_size = '128M'
        elif chunk <= 32:

            # 2G < buffer_pool <= 4G
            self.innodb_log_file_size = '256M'
            self.innodb_log_buffer_size = '256M'
        elif chunk <= 64:

            # 4G < buffer_pool <= 8G
            self.innodb_log_file_size = '256M'
            self.innodb_log_buffer_size = '256M'
        else:

            # 8G < buffer_pool
            self.innodb_log_file_size = '256M'
            self.innodb_log_buffer_size = '2G'

        # 设置最大连接数
        self.max_connections = chunk * 8
        if self.max_connections <= 128:
            self.max_connections = 128
        elif self.max_connections >= 2048:
            self.max_connections = 2048

    def _config_disk(self):
        """
        磁盘目前还不做配置
        """
        pass

    def auto_config(self):
        """
        根据给定的物理参数配置数据库
        """
        self._config_cpus()
        self._config_mems()
        self._config_disk()

    def enable_mgr(self, local_address: str = "127.0.0.1:33061",
                   group_seeds: str = "127.0.0.1:33061,127.0.0.1:33062,127.0.0.1:33063"):
        """
        启用 MGR
        """
        logger = self.logger.getChild("enable_mgr")
        logger.debug("enable mysql group replication")
        self.is_mgr = True

        self.group_replication_local_address = local_address
        self.group_replication_group_seeds = group_seeds

    def set_template(self, template="mysql-8.0.18.cnf.jinja"):
        """
        设置所要使用的配置文件模板
        """
        logger = self.logger.getChild('set_template')

        # 检查配置文件模板是否存在
        if not checkings.is_file_exists(os.path.join(cnf.base_dir, 'etc/templates/', template)):

            # 配置文件模板不存在就报错
            logger.error(f"mysql cnf template file '{template}' not exists")
            raise errors.FileNotExistsError(template)

        logger.info(f"using template file '{template}' ")

        # 加上下划线，防止被渲染到配置文件中去
        self._template = template

    def set_output(self, output="/etc/my-3306.cnf"):
        """
        设置配置要被渲染到的目标文件
        """
        logger = self.logger.getChild('set_output')

        # 检查(要求目标文件不存在)
        if checkings.is_file_exists(output):

            # 存在就报错
            logger.error(f"output file '{output}' already exists")
            raise errors.FileAlreadyExistsError(output)

        self._output = output

    def render(self):
        """
        渲染配置文件模板
        """
        logger = self.logger.getChild("render")
        logger.debug(f"start render mysql cnf file using {self._template}")

        # 从 /usr/local/dbm-agent/etc/templates/ 目录下找配置文件模板
        template_dir = os.path.join(self.dbma.base_dir, 'etc/templates/')
        self.tmpl = Environment(loader=FileSystemLoader(
            searchpath=template_dir)).get_template(self._template)

        # 配置全局字典
        self.auto_config()
        self.tmpl.globals = self.__dict__

        with common.sudo(f"render config file {self._output}"):
            with open(f"{self._output}", 'w') as cnf:
                cnf.write(self.tmpl.render())

        logger.info(f"render mysql config file {self._output}")


class MyCnfInitRender(MyCnfRender):
    """
    专门为 init 阶段生成配置文件所用的 render
    """
    logger = logger.getChild('MyCnfInitRender')

    def render_template_file(self):
        """
        渲染
        """
        logger = self.logger.getChild('render_template_file')
        logger.debug("prepare render init config file")

        # 配置文件要渲染到的位置
        init_cnf = "/tmp/mysql-init.cnf"

        # 要使用的模板
        template = 'mysql-8.0-init-only.jinja'
        logger.info(f"using template '{template}' ")

        self.set_output(init_cnf)
        self.set_template(template)
        self.render()

        logger.info("render template file complete")


class MyCnfMSRender(MyCnfRender):
    """
    专门为单机、主从 环境生成配置文件所用的 render
    """
    logger = logger.getChild('MyCnfMSRender')

    def render_template_file(self):
        """
        渲染适合单机、主从的生产环境配置文件
        """
        logger = self.logger.getChild('render_template_file')
        logger.debug("prepare render master | master-slave config file")

        # 配置文件要渲染到的位置
        out_cnf_file = f"/etc/my-{self.port}.cnf"

        # 要使用的模板
        pattern = r"8.0.\d\d"
        version_number = re.search(pattern, self.basedir).group(0)

        template = f'mysql-{version_number}.cnf.jinja'
        logger.info(f"using template '{template}' ")

        self.set_output(out_cnf_file)
        self.set_template(template)
        self.render()

        logger.info("render template file complete")


class MyCnfMGRRender(MyCnfRender):
    """
    专门为 MGR 环境生成配置文件所用的 render
    """
    logger = logger.getChild('MyCnfMGRRender')

    def __init__(self, basedir="/usr/local/mysql-8.0.17-linux-glibc2.12-x86_64/",
                 datadir="/database/mysql/data/3306/", binlogdir="/binlog/mysql/binlog/3306/",
                 max_mem=128, cores=1, port=3306, user="mysql3306", local_address: str = None,
                 group_seeds: str = None
                 ):
        """

        """
        MyCnfRender.__init__(self, basedir=basedir, datadir=datadir, binlogdir=binlogdir, max_mem=max_mem,
                             cores=cores, port=port, user=user)

        # group_seeds 和 local_address 都不能是 None
        if local_address is None or group_seeds is None:
            raise ValueError(
                "args('local_address','group_seeds') in MyCnfMGRRender.__init__ must be not None")

        self.group_replication_local_address = local_address
        self.group_replication_group_seeds = group_seeds
        self.group_replication_consistency = "BEFORE_ON_PRIMARY_FAILOVER"
        self.is_mgr = True

    def render_template_file(self):
        """
        渲染适用于 MGR 的生产环境配置文件
        """
        logger = self.logger.getChild('render_template_file')
        logger.debug("prepare render MGR config file")

        # 配置文件要渲染到的位置
        out_cnf_file = f"/etc/my-{self.port}.cnf"

        # 要使用的模板
        pattern = r"8.0.\d\d"
        version_number = re.search(pattern, self.basedir).group(0)

        template = f'mysql-{version_number}.cnf.jinja'
        logger.info(f"using template '{template}' ")

        self.set_output(out_cnf_file)
        self.set_template(template)
        self.render()

        logger.info("render template file complete")


class MySQLSystemdRender(object):
    """
    渲染 systemd 会用到的 mysqld-{self.port}.service 配置文件
    """
    logger = logger.getChild("MySQLSystemdRender")

    def __init__(self, basedir="/usr/local/mysql-8.0.17-linux-glibc2.12-x86_64", port=3306, user="mysql3306"):
        """
        """
        self.basedir = basedir
        self.port = port
        self.user = user

    def set_template(self, template_file="mysqld.service.jinja"):
        """
        设置渲染时所要的模板
        """
        logger = self.logger.getChild("set_template")

        logger.debug(f"using template '{template_file}' ")
        template_dir = os.path.join(cnf.base_dir, 'etc/templates/')
        self.tmpl = Environment(loader=FileSystemLoader(
            searchpath=template_dir)).get_template(template_file)

    def set_output(self, output_file="/usr/lib/systemd/system/mysqld-3306.service"):
        """
        设置输出的目标文件
        """
        logger = self.logger.getChild("set_output")

        logger.debug(f"render systemd config to '{output_file}' ")
        self._output = output_file

    def render(self):
        """
        渲染 MySQL 的 systemd 配置文件
        """
        logger = self.logger.getChild('render')
        logger.debug("start render mysql systemd config file")

        if not hasattr(self, 'tmpl'):

            # 如果还没有 template 对象就运行它
            self.set_template()

        if not hasattr(self, '_output'):

            # 如果还没有 _output
            self.set_output()

        # 配置全局字典
        self.tmpl.globals = self.__dict__

        with common.sudo(f"render systemd config file /usr/lib/systemd/system/"):
            with open(self._output, 'w') as cnf:
                cnf.write(self.tmpl.render())

        logger.info("render systemd config file complete")


class MySQLInstallerMixin(object):
    """
    抽象出所有 MYSQL 安装&卸载过程中所有的操作
    """

    def _get_mysql_version(self):
        """
        根据 self.pkg 返回 MySQL 的版本信息
        """
        logger = self.logger.getChild('_get_mysql_version')

        if self.pkg is None:

            # 如果 pkg 变量的值是 None 说明这个有问题、返回 None
            logger.error("variable self.pkg is None,this is not normal")
            return None
        else:
            return self.pkg.replace('.tar.gz', '').replace('.tar.xz', '')

    def _auto_config(self):
        """
        在执行完成成检查之后，就可以保存实例的各个属性是正确的，于是就可以根据这些属性来生成依赖属性了
        """
        self.basedir = f"/usr/local/{self._get_mysql_version()}"
        self.datadir = f"/database/mysql/data/{self.port}"
        self.binlogdir = f"/binlog/mysql/binlog/{self.port}"
        self.backupdir = f"/backup/mysql/backup/{self.port}"
        self.user = f"mysql{self.port}"

    def _basic_checks(self):
        """
        安装 MySQL 最基本的检查

        @NotSupportedMySQLVersionError
        @PortIsInUseError
        @UserAlreadyExistsError
        @FileAlreadyExistsError
        @DirecotryAlreadyExistsError
        @FileNotExistsError
        """
        logger = self.logger.getChild('basic_checks')

        # 检查项1、安装包是不是存在
        # 检查安装包是否存在、如果安装包不存在，但是 /usr/local/ 目录下有对应的解压后的目录，也算是安装包存在
        # mysql 安装包的版本 --> mysql-8.0.17-linux-glibc2.12-x86_64
        mysql_version = self._get_mysql_version()

        # mysql 安装之后的完整目录 /usr/local/mysql-8.0.17-linux-glibc2.12-x86_64
        mysql_installed_dir = os.path.join(
            self.dbma.mysql_install_dir, self._get_mysql_version())

        # 安装包全路径
        pkg_full_path = os.path.join(self.dbma.base_dir, f'pkg/{self.pkg}')

        if checkings.is_directory_exists(mysql_installed_dir) or checkings.is_file_exists(pkg_full_path):

            # 安装包存在 或者存在解压后的目录
            pass
        else:
            logger.error(f"package '{self.pkg}'' not exits")
            raise errors.NotSupportedMySQLVersionError(self.pkg)

        # 检查项2、端口是不是没有被占用
        if checkings.is_port_in_use(port=self.port):

            # 给定的端口在使用中、直接报错
            logger.error(f"port '{self.port}' is in use")
            raise errors.PortIsInUseError(self.port)

        # 检查项3、用户是否存在
        user = f"mysql{self.port}"
        if checkings.is_user_exists(user):
            # 如果用户已经存在就报错
            logger.error(f"user '{user}' exists")
            raise errors.UserAlreadyExistsError(user)

        # 检查项4、配置文件是否存在
        mysql_cnf = f'/etc/my-{self.port}.cnf'
        if checkings.is_file_exists(mysql_cnf):

            # mysql 配置文件存在直接报错
            logger.error(f"mysql config file '{mysql_cnf}' already exists ")
            raise errors.FileAlreadyExistsError(mysql_cnf)

        # 检查项5、数据目录是否存在
        mysql_data_dir = f"/database/mysql/data/{self.port}"
        if checkings.is_directory_exists(mysql_data_dir):

            # mysql 数据目录存在
            logger.error(f"datadir '{mysql_data_dir}' is exists")
            raise errors.DirecotryAlreadyExistsError(mysql_data_dir)

        # 检查项6、binlog 目录是否存在
        mysql_binlog_dir = f"/binlog/mysql/binlog/{self.port}"
        if checkings.is_directory_exists(mysql_binlog_dir):

            # binlog 目录已经存在
            logger.error(
                f"mysql binlog  directory '{mysql_binlog_dir}' exists")
            raise errors.DirecotryAlreadyExistsError(mysql_binlog_dir)

        # 检查项7、版本号是否被直接
        mysql_version = self._get_mysql_version()
        patter = r"mysql(-commercial){0,1}-(8.0.\d\d)-linux-glibc2.12-x86_64"
        m = re.search(patter, mysql_version)
        if m:

            # 说明匹配正常、下一步就是要检查版本号是不是 >= 8.0.17
            version_number = m.group(2)
            if version_number < '8.0.17':

                # 最少要是 8.0.17 版本才会被 dbm-agent 支持
                logger.error(f"mysql version must big then '{mysql_version}'")
                raise errors.NotSupportedMySQLVersionError(mysql_version)
        else:

            # 不满足 MySQL 二进制安装包的命名模式
            logger.error(f"not supported mysql version '{mysql_version}' ")
            raise errors.NotSupportedMySQLVersionError(mysql_version)

        # 检查项8、与给定版本匹配的配置文件模板要存在
        cnf_template = os.path.join(
            self.dbma.base_dir, 'etc/templates', f"mysql-{version_number}.cnf.jinja")
        if not checkings.is_file_exists(cnf_template):

            # 配置文件模板不存在
            logger.error(f"config file template '{cnf_template}' not exists")
            raise errors.FileNotExistsError(cnf_template)

        # 检查项9、初始化模板是否存在
        init_template = os.path.join(
            self.dbma.base_dir, 'etc/templates', f"mysql-8.0-init-only.jinja")
        if not checkings.is_file_exists(init_template):

            # 初始化配置文件模板不存在
            logger.error(f"mysql init template not exists '{init_template}' ")
            raise errors.FileAlreadyExistsError(init_template)

        # 完成所有的检查之后就可以生成信赖属性了
        self._auto_config()

    def _extract_install_pgk(self):
        """
        解压安装包到 /usr/local/

        @FileNotExistsError
        """
        logger = self.logger.getChild('_extract_install_pgk')

        # 虽然 _basic_checks 已经对安装包的存在性做了检查，但是 dbm-agent 是一个数据库管理程序，重要的是稳，所以在这里还要进行二次检查

        logger.debug("start extract mysql install package")

        # 如果解压后的目录已经存在，那么就直接完成
        if checkings.is_directory_exists(self.basedir):
            logger.debug(f"mysql has been installed")
            return

        # 执行到这里说明 mysql 在此之前并没有被安装
        pkg_full_path = os.path.join(self.dbma.base_dir, f'pkg/{self.pkg}')
        if not checkings.is_file_exists(pkg_full_path):

            # 要在 run 中处理
            logger.error(
                f"mysql install package not exists '{pkg_full_path}' ")
            raise errors.FileNotExistsError(pkg_full_path)

        # 解压安装包
        with common.sudo(f"extract mysql install package to {self.dbma.mysql_install_dir}"):
            shutil.unpack_archive(pkg_full_path, self.dbma.mysql_install_dir)
            common.recursive_change_owner(
                path=self.basedir, user='root', group='mysql')

        logger.info("extract mysql package completed")

    def _create_mysql_user(self):
        """
        创建 mysql 用户和组

        @UserAlreadyExistsError
        """
        logger = self.logger.getChild('_create_mysql_user')

        logger.debug(f"start create user '{self.user}' ")

        # 双重检测
        if checkings.is_user_exists(self.user):

            # 如果用户已经存在就报错
            logger.error(f"user '{self.user}' already exists")
            raise errors.UserAlreadyExistsError(self.user)

        with common.sudo(f"create mysql user {self.user}"):
            common.create_user(self.user)

        logger.info(f"create user '{self.user}' complete")

    def _create_data_dir(self):
        """
        创建数据目录

        @DirecotryAlreadyExistsError
        """
        logger = self.logger.getChild('_create_data_dir')

        logger.debug(f"start create datadir '{self.datadir}' ")

        if checkings.is_directory_exists(self.datadir):

            # 如果 datadir 已经存在就报错
            logger.error(f"datadir '{self.datadir}' alread exists")
            raise errors.DirecotryAlreadyExistsError(self.datadir)

        # 执行到这里说明 datadir 不存在、那么就要创建它
        pathlib.Path(self.datadir).mkdir(parents=True)

        common.recursive_change_owner(self.datadir, user=self.user)

        #
        logger.info(f"create datadir '{self.datadir}' complete")

    def _create_binlog_dir(self):
        """
        创建 binlog 目录

        @DirecotryAlreadyExistsError
        """
        logger = self.logger.getChild('_create_binlog_dir')

        logger.debug(f"start create binlog dir '{self.binlogdir}' ")

        if checkings.is_directory_exists(self.binlogdir):

            # 如果 binlog  目录已经存在就报错
            logger.error(f"binary log dir '{self.binlogdir}' alread exists")
            raise errors.DirecotryAlreadyExistsError(self.binlogdir)

        # 执行到这里说明 binlog 目录不存在、那么就要创建它
        pathlib.Path(self.binlogdir).mkdir(parents=True)
        common.recursive_change_owner(self.binlogdir, user=self.user)
        #
        logger.info(f"create binary dir '{self.binlogdir}' complete")

    def _create_backup_dir(self):
        """
        创建备份目录

        @DirecotryAlreadyExistsError
        """
        logger = self.logger.getChild('_create_backup_dir')

        logger.debug(f"start create backup dir '{self.backupdir}' ")

        if checkings.is_directory_exists(self.backupdir):

            # 如果 binlog  目录已经存在就报错
            logger.error(f"backup log dir '{self.backupdir}' alread exists")
            raise errors.DirecotryAlreadyExistsError(self.backupdir)

        # 执行到这里说明 binlog 目录不存在、那么就要创建它
        pathlib.Path(self.backupdir).mkdir(parents=True)
        common.recursive_change_owner(self.backupdir, user=self.user)
        #
        logger.info(f"create backup dir '{self.backupdir}' complete")

    def _render_init_cnf(self):
        """
        渲染一份 init 传用的配置文件到 /tmp/mysql-init.cnf
        """
        logger = self.logger.getChild('_render_init_cnf')

        # 创建渲染对象
        render = MyCnfInitRender(basedir=self.basedir, datadir=self.datadir, binlogdir=self.binlogdir,
                                 max_mem=self.max_mem, cores=self.cores, port=self.port, user=self.user)
        render.render_template_file()

    def _render_production_cnf(self):
        """
        渲染生产环境配置文件
        """
        logger = self.logger.getChild('_render_production_cnf')

        render = MyCnfMSRender(basedir=self.basedir, datadir=self.datadir, binlogdir=self.binlogdir,
                               max_mem=self.max_mem, cores=self.cores, port=self.port, user=self.user)

        # 开始渲染
        render.render_template_file()
        logger.info("render production cnf complete")

    def _render_mgr_cnf(self):
        """
        渲染 MGR 生产环境的配置文件
        """
        logger = self.logger.getChild('_render_mgr_cnf')
        logger.debug(f"prepare render mgr config file ")

        # 创建配置文件生成器
        render = MyCnfMGRRender(basedir=self.basedir, datadir=self.datadir, binlogdir=self.binlogdir,
                                max_mem=self.max_mem, cores=self.cores, port=self.port, user=self.user,
                                local_address=self.local_address, group_seeds=self.group_seeds)
        render.render_template_file()

    def _init_database(self):
        """
        初始化数据库
        """
        logger = self.logger.getChild('_init_database')

        # 先生成数据库初始化专用配置文件(mysql-8.0.18 版本及以上版本在 --initialize-insecure 时已经不再加载非必要插件)
        # 所以这里要生成两份配置文件一份用于初始化、一份用于运行
        logger.debug("start init database with --initialize-insecure")

        # 如果初始化文件存在就不创建
        if not checkings.is_file_exists("/tmp/mysql-init.cnf"):
            self._render_init_cnf()

        # 如果生产环境配置文件存在就不创建
        if not checkings.is_file_exists(f"/etc/my-{self.port}.cnf"):
            if hasattr(self, 'is_mgr'):
                if self.is_mgr == False:
                    self._render_production_cnf()
            else:
                self._render_production_cnf()

        # 强行渲染 MGR 的配置文件
        if not checkings.is_file_exists(f"/etc/my-{self.port}.cnf"):
            if hasattr(self, 'is_mgr'):
                if self.is_mgr == True:
                    self._render_mgr_cnf()

        init_file = os.path.join(self.dbma.base_dir, 'etc/init-users.sql')

        with common.sudo("init database"):
            args = [f'{self.basedir}/bin/mysqld', f'--defaults-file=/tmp/mysql-init.cnf',
                    '--initialize-insecure', f'--user=mysql{self.port}', f'--init-file={init_file}']
            logger.info(args)
            subprocess.run(args, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)

        # 删除初始化文件
        logger.debug("remove /tmp/mysql-init.cnf")
        os.remove('/tmp/mysql-init.cnf')

        logger.info("init database complete")

    def _config_systemd(self):
        """
        配置 mysql 通过 systemd 启动
        """
        logger = self.logger.getChild('_config_systemd')

        render = MySQLSystemdRender(
            basedir=self.basedir, port=self.port, user=self.user)

        # 配置
        render.set_template("mysqld.service.jinja")
        render.set_output(
            f"/usr/lib/systemd/system/mysqld-{self.port}.service")

        render.render()
        logger.info("mysql systemd config complete")

    def _enable_mysql(self):
        """
        MySQL 开机自启动
        """
        logger = self.logger.getChild("_enable_mysql")
        with common.sudo(f"enable systemd mysqld-{self.port}"):
            subprocess.run(['systemctl daemon-reload'], shell=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(
                [f'systemctl enable mysqld-{self.port}'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info("config mysql auto start on boot complete")

    def _start_mysql(self):
        """
        启动 MySQL 服务
        """
        logger = self.logger.getChild("_start_mysql")
        with common.sudo(f"enable systemd mysqld-{self.port}"):
            subprocess.run(
                [f'systemctl start mysqld-{self.port}'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        logger.debug("wait mysql start")

        # 最多等 30 秒
        wait_counter = 0
        while wait_counter <= 30:
            if not checkings.is_port_in_use(ip='127.0.0.1', port=self.port):

                # 执行到这里说明端口还没有被监听
                wait_counter = wait_counter + 1
                time.sleep(1)
            else:

                # 监听已经启动就 break
                break
        else:
            logger.warning(
                f"mysql does not listening {self.port} ,contact mysql-dba for help !!!")
            return

        logger.info("start mysql complete")

    def _export_path(self):
        """
        导出 PATH 环境变量
        """
        logger = self.logger.getChild('_export_path')

        common.config_path(f"{self.basedir}/bin/", self.user)

        logger.info("export path complete")

    def _export_so(self):
        """
        导出 MySQL 共享库
        """
        logger = self.logger.getChild('_export_so')
        export_file = os.path.join(
            '/etc/ld.so.conf.d', f'{self._get_mysql_version()}.conf')
        if not checkings.is_file_exists(export_file):
            with common.sudo("export so file"):
                with open(export_file, 'w') as sofile:
                    sofile.write(f"{self.basedir}/lib\n")
            logger.info("export so file complete")
        else:
            logger.info("so file has been exported")

    def _export_header_file(self):
        """
        导出头文件
        """
        logger = self.logger.getChild("_export_header_file")
        with common.sudo("export header file"):
            link = f"/usr/include/{self._get_mysql_version()}"
            src = os.path.join(f"{self.basedir}", "include")
            if not os.path.islink(link):
                os.symlink(src, link)

        logger.info("export header file complete")

    def install(self):
        """
        安装 MySQL 实例
        """
        logger = self.logger.getChild("install")

        # 准备进行基本的验证
        logger.info("execute checkings for install mysql")
        try:
            self._basic_checks()
        except Exception as err:
            logger.error(f"{err}")
            self.is_successful_complete = False
            return

        # 创建用户
        self._create_mysql_user()

        # 解压安装包
        self._extract_install_pgk()

        # 创建数据目录、binlog目录、备份目录
        self._create_data_dir()
        self._create_binlog_dir()
        self._create_backup_dir()

        # 初始化数据库(渲染配置文件的逻辑被包含在了里面)
        self._init_database()

        # 配置服务的开机启动
        self._config_systemd()
        self._enable_mysql()
        self._start_mysql()

        # 导出 PHTH环境变量、导出头文件、导出共享库
        self._export_path()
        self._export_header_file()
        self._export_so()

        # 标记为安装成功
        self.is_successful_complete = True

        logger.info("install mysql single instance complete")


class MySQLUninstallerMixin(object):
    """
    实现 MySQL 卸载相关的逻辑
    """

    def _basic_checks(self):
        """
        卸载前一些基本的检查
        """
        logger = self.logger.getChild('_basic_checks')

        logger.debug(f"doing checks for uninstall mysql instance {self.port}")
        # 检查项1、端口不能在使用中
        if checkings.is_port_in_use(ip="127.0.0.1", port=self.port):

            # 卸载前要确保端口没有被占用
            logger.error(f"port '{self.port}' is in use")
            raise errors.PortIsInUseError(self.port)

        # 检查项2、pid 文件也要不存在 这两项有一定的重复，主要还是为了稳
        if checkings.is_file_exists(f"/tmp/mysql-{self.port}.pid"):
            logger.error(f"pid file  '/tmp/mysql-{self.port}.pid' exists")
            raise errors.FileAlreadyExistsError(f"/tmp/mysql-{self.port}.pid")

    def uninstall(self):
        """
        """
        logger = self.logger.getChild('uninstall')

        try:
            self._basic_checks()
        except errors.PortIsInUseError as err:
            logger.warning(
                f"mysql is runing,want stop it? 'systemctl stop mysqld-{self.port}' ")
            return
        except errors.FileAlreadyExistsError as err:
            logger.warning(
                f"mysql is runing,want stop it? 'systemctl stop mysqld-{self.port}' ")
            return
        except Exception as err:
            logger.error(
                f"undefined exception occure,can not remove this mysql instance {err}")
            return

        # 能执行到这里说明数据库实例已经停止运行
        logger.info(f"start drop instance mysqld-{self.port}")
        try:
            # 删除用户
            if checkings.is_user_exists(self.user):
                common.delete_user(self.user)
                logger.info(f"user '{self.user}' deleted")

            with common.sudo(f"drop instance {self.port}"):
                # 删除数据目录
                if checkings.is_directory_exists(self.datadir):
                    shutil.rmtree(self.datadir)
                    logger.info(f"data directory '{self.datadir}' deleted")

                # 删除二进制日志
                if checkings.is_directory_exists(self.binlogdir):
                    shutil.rmtree(self.binlogdir)
                    logger.info(f"binlog directory '{self.binlogdir}' deleted")

                # 删除备份目录
                if checkings.is_directory_exists(self.backupdir):
                    shutil.rmtree(self.backupdir)
                    logger.info(f"backup direcotry '{self.backupdir}' deleted")

                # 去除开机自启动
                subprocess.run(
                    f"systemctl disable mysqld-{self.port}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                # 删除配置文件
                if checkings.is_file_exists(self.cnf_file):
                    os.remove(self.cnf_file)

                # 删除 systemd 配置文件
                if checkings.is_file_exists(self.systemd_file):
                    os.remove(self.systemd_file)

                logger.info(f"drop mysql instance {self.port} complete")

        except Exception as err:
            logger.error(err)


class MySQLClonerMixin(object):
    """
    MySQL 克隆相关的操作
    """

    def _local_clone_checks(self):
        """
        在进行本地克隆之前要进行的检查

        @MySQLIsNotRunningError
        @Exception
        """
        logger = self.logger.getChild("_local_clone_checks")
        # 检查 MySQL 数据库是否在运行
        if not checkings.is_port_in_use(ip='127.0.0.1', port=self.port):

            # 如果端口还没有在使用，说明本地克隆的条件不成立
            logger.error(f"mysqld-{self.port} is not runing")
            raise errors.MySQLIsNotRunningError(f"mysqld-{self.port}")

        # 检查 MySQL 是否有权限连接到要克隆的实例
        cnx = None
        try:
            cnx = connector.connect(
                host=self.host, port=self.port, user=self.clone_user, password=self.clone_password)
            cursor = cnx.cursor(dictionary=True)
            cursor.execute("select 1 as ok")
            data = cursor.fetchone()

        except Exception as err:
            logger.error(
                f"'cloneuser' conect to {self.host} {self.port} faile innner error {err}")
            raise err

        finally:
            if hasattr(cnx, 'close'):
                cnx.close()

    def _remote_clone_checks(self):
        """
        进行远程克隆之前的检查
        """
        # 1、远程实例要能连接的上
        cnx = None
        logger = self.logger.getChild('_remote_clone_checks')
        try:
            logger.debug("")
            cnx = connector.connect(
                host=self.host, port=self.port, user=self.clone_user, password=self.clone_password)
            cursor = cnx.cursor(dictionary=True)
            cursor.execute("select 1 as ok;")
            data = cursor.fetchone()
        except Exception as err:

            # 如果出错就直接报异常
            logger.error(f"got error during checking remote instance {err}")
            raise err
        finally:
            if hasattr(cnx, 'close'):
                cnx.close()

        # 2、本地实例要求不存在
        if checkings.is_port_in_use(ip="127.0.0.1", port=self.port):
            logger.error(f"local instance mysqld-{self.port} is runing")
            raise errors.PortIsInUseError(f"127.0.0.1:{self.port} is runing")

        logger.debug("_remote_clone_checks completed")


class MySQLShellInstallerMixin(object):
    """
    自动化安装 mysql-shell-8.0.xx 版本
    """

    def _basic_checks(self):
        """
        安装 mysql-shell-8.0.xx 前的一些检查
        """
        logger = self.logger.getChild("_basic_checks")

        # 检查项1、给定的安装文件是否存在
        if not checkings.is_file_exists(self.mysql_shell_pkg_full_path) and not checkings.is_directory_exists(self.mysql_shell_basedir):

            # 安装包不存在，并且也没有解压后的目录
            logger.error(f"file '{self.mysql_shell_pkg_full_path}' not exists")
            raise errors.FileNotExistsError(self.mysql_shell_pkg_full_path)

    @property
    def _is_shell_installed(self):
        """
        MySQL-shell 是否已经完成安装
        """
        return checkings.is_directory_exists(self.mysql_shell_basedir)

    def _extract_install_pkg(self):
        """
        解压安装包到 /usr/local/
        """
        logger = self.logger.getChild('_extract_install_pkg')
        if self._is_shell_installed == True:
            logger.info("mysql-shell has been installed")
            return

        # 能执行到这里说明 mysql-shell 还没有被安装

        # 解压安装包
        with common.sudo(f"extract mysql-shell install package to {self.dbma.mysql_install_dir}"):
            shutil.unpack_archive(
                self.mysql_shell_pkg_full_path, self.dbma.mysql_install_dir)
            common.recursive_change_owner(
                path=self.mysql_shell_basedir, user='root', group='mysql')

        logger.info("extract mysql-shell complete")

    def _export_path(self):
        """
        导出 PATH 环境变量
        """
        logger = self.logger.getChild("_export_path")

        # 计算出 export
        shell_bin_path = os.path.join(self.mysql_shell_basedir, 'bin')
        line = f"export PATH={shell_bin_path}:$PATH"

        # 检查 path 是否已经有导出
        with common.sudo("export mysql-shell to path"):
            with open('/etc/profile') as f_profile:
                logger.info("mysql-shell path not exported")
                is_exported = line in f_profile

        # 如果没有
        if is_exported == False:
            with common.sudo("export mysql-shell to path"):
                with open('/etc/profile', 'a') as f_profile:
                    f_profile.write('\n')
                    f_profile.write(line)
                    f_profile.write('\n')

                logger.info("mysql-shell path exported")

        logger.info("export mysql-shell path complete")

    def install(self):
        """
        """
        logger = self.logger.getChild("install")

        # 检查
        try:
            self._basic_checks()
        except Exception as err:
            self.is_successful_complete = False
            logger.error(f"{err}")
            return

        # 解压
        self._extract_install_pkg()

        # 导出 path
        self._export_path()

        self.is_successful_complete = True

        logger.info("install mysql-shell complete")


class MySQLInstaller(threading.Thread, MySQLInstallerMixin):
    """
    实现单机环境的安装
    """
    logger = logger.getChild('SingleInstanceInstaller')

    def __init__(self, pkg="mysql-8.0.18-linux-glibc2.12-x86_64.tar.xz",
                 port=3306, max_mem=128, cores=1, name='im', daemon=True):
        """

        """
        threading.Thread.__init__(self, name=name, daemon=daemon)

        logger = self.logger.getChild('__init__')

        # 取得 dbma 的配置文件对象
        self.dbma = cnf

        # 写本次安装相关的配置信息
        self.pkg = pkg
        self.port = port
        self.max_mem = max_mem
        self.cores = cores

        self.is_successful_complete = False

    def after_complete(self):
        """
        任务完成之后要执行的操作
        """
        pass

    def run(self):
        """
        """
        logger = self.logger.getChild('run')
        try:
            self.install()
            self.after_complete()
        except Exception as err:
            logger.error(
                f"exception occur during install mysql single instance {err}")


class MySQLUninstaller(threading.Thread, MySQLUninstallerMixin):
    """
    为删除操作单独开一个线程
    """
    logger = logger.getChild('MysqlUninstaller')

    def __init__(self, port=3306):
        """
        """
        logger = self.logger.getChild('MysqlUninstaller')

        threading.Thread.__init__(self, name='um', daemon=True)
        self.port = port
        self.user = f"mysql{self.port}"
        self.datadir = f"/database/mysql/data/{self.port}"
        self.cnf_file = f"/etc/my-{self.port}.cnf"
        self.binlogdir = f"/binlog/mysql/binlog/{self.port}"
        self.backupdir = f"/backup/mysql/backup/{self.port}"
        self.systemd_file = f"/usr/lib/systemd/system/mysqld-{self.port}.service"

    def after_complete(self):
        """
        任务完成之后要执行的操作
        """
        pass

    def run(self):
        """
        """

        self.uninstall()


class MySQLCloner(threading.Thread, MySQLClonerMixin, MySQLInstallerMixin):
    """
    实现对 MYSQL 实例的克隆，同时支持本地克隆和远程克隆两种方式

    1、如果是本地克隆可以直接开始克隆

    2、如果是远程克隆
    2.1、在本地安装数据库实例
    2.2、执行远程克隆
    2.3、重启实例
    2.4、检查是否正确完成
    """
    logger = logger.getChild('MySQLCloner')

    def __init__(self, pkg="mysql-8.0.18-linux-glibc2.12-x86_64.tar.xz",
                 host="127.0.0.1", port=3306, clone_user="cloneuser", clone_password="dbma@0352", max_mem=128, cores=1, name='cm', daemon=True):
        """

        可以根据 host 的地址来决定是本地克隆还是远程克隆
        """
        threading.Thread.__init__(self, name=name, daemon=daemon)
        logger.debug(
            f"cloner instance init args pkg={pkg} host={host} port={port} user={clone_user} password={clone_password} max_mem={max_mem} cores={cores} ")

        # 取得 dbma 的配置文件对象
        self.dbma = cnf
        self.pkg = pkg

        self.host = host
        self.port = port
        self.clone_user = clone_user
        self.clone_password = clone_password

        self.max_mem = max_mem
        self.cores = cores

        self.now = datetime.now().isoformat()
        self.is_successful_complete = False

    def _is_remote_mgr_enabled(self):
        """
        要克隆远程主机是否开启 MGR

        通过检查是否存在 group_replication_group_name 变量来判断是否有开启 MGR
        """
        cnx = None
        try:
            cnx = connector.connect(
                host=self.host, port=self.port, user=self.clone_user, password=self.clone_password)
            cursor = cnx.cursor(dictionary=True)
            cursor.execute(
                "show global variables like 'group_replication_group_name'")
            data = cursor.fetchone()
            is_mgr_enabled = True if data is not None else False
        except Exception as err:
            is_mgr_enabled = False
        finally:
            if hasattr(cnx, 'close'):
                cnx.close()

        self.is_mgr = is_mgr_enabled

        if type(self) == MySQLBuildSlave:

            # 如果只是创建 slave 强行把 mgr 切为 false
            self.is_mgr = False

    def local_clone(self):
        """
        克隆当前主机上的实例
        """
        logger = self.logger.getChild("local_clone")
        logger.info(f"start clone mysqld-{self.port}")
        logger.info(
            f"save backup files to '/backup/mysql/backup/{self.port}/{self.now}'")
        try:
            # 如果在检查的时候就遇到了异常那就直接报
            self._local_clone_checks()
        except Exception as err:
            logger.error(
                f"can't clone current instance mysqld{self.port} inner error {err}")
            return

        cnx = None
        # 更新一下备份目录的权限

        with common.sudo("change backup directory's owner"):
            shutil.chown(
                f"/backup/mysql/backup/{self.port}/", f'mysql{self.port}')

        try:
            cnx = connector.connect(
                host='127.0.0.1', port=self.port, user=self.clone_user, password=self.clone_password)
            cursor = cnx.cursor(dictionary=True)
            local_clone_sql = f"CLONE LOCAL DATA DIRECTORY = '/backup/mysql/backup/{self.port}/{self.now}' "
            cursor.execute(local_clone_sql)
        except Exception as err:
            logger.error(f"exception occur during local clone {err}")
            raise errors.LocalCloneFaileError(f"{err}")
        finally:
            if hasattr(cnx, 'close'):
                cnx.close()

        logger.info(f"locale clone 'mysqld-{self.port}' complete")

    def remote_clone(self):
        """
        克隆远程实例
        """
        logger = self.logger.getChild("remote_clone")
        logger.debug("start remonte clone")
        try:
            self._remote_clone_checks()
        except Exception as err:

            # 检查时遇到错误，clone直接失败
            logger.error(f"remote clone check fail {err}")
            return

        # 如果可以执行到这里，说明通过了检查
        # 第一步：在当前主机上安装上一个新的实例
        # 准备进行基本的验证
        logger.info("execute checkings for install mysql")
        try:
            self._basic_checks()
        except Exception as err:
            logger.error(f"{err}")
            return

        # 验证远程实例是不是 MGR
        self._is_remote_mgr_enabled()
        if self.is_mgr == True:
            logger.warning(
                "remonte instance is an mgr node, dbm well render mgr options")

        # 安装一个本地的 MYSQL 实例
        self.install()

        # 第二步：连接上本地实例，然后从远程克隆
        cnx = None
        try:

            # 连接到本地实例并设置它的 donor list
            cnx = connector.connect(
                host="127.0.0.1", port=self.port, user=self.clone_user, password=self.clone_password)
            donor_sql = f"set @@global.clone_valid_donor_list='{self.host}:{self.port}';"
            cursor = cnx.cursor(dictionary=True)
            logger.info(f"prepare execute '{donor_sql}' ")
            cursor.execute(donor_sql)
            [_ for _ in cursor]
            # 发起 clone 语句
            clone_sql = f"clone instance from {self.clone_user}@'{self.host}':{self.port} identified by '{self.clone_password}';"
            logger.info(f"prepare execute '{clone_sql}' ")
            cursor.execute(clone_sql)

        except Exception as err:
            logger.info(f"got some error during remonte clone {err}")
            return
        finally:
            if hasattr(cnx, 'close'):
                cnx.close()

        # 可以执行到这里说明 remote_clone 成功了
        logger.info(
            "remote clone complete (mysql will auto restart,please wait)")
        self.is_successful_complete = True

    def run(self):
        """
        """
        if self.host == '127.0.0.1':
            self.local_clone()
        else:
            self.remote_clone()


class MySQLBuildSlave(MySQLCloner):
    """
    完成 slave 的自动化建设

    1、remote-clone 出一个完整的 master 复本
    2、change master to
    3、start slave
    """
    logger = logger.getChild('MySQLBuildSlave')

    def __init__(self, pkg="mysql-8.0.18-linux-glibc2.12-x86_64.tar.xz",
                 host="127.0.0.1", port=3306, clone_user="cloneuser", clone_password="dbma@0352",
                 replication_user="repluser", replication_password="dbma@0352",
                 max_mem=128, cores=1, name='cm', daemon=True):

        MySQLCloner.__init__(self, pkg=pkg, host=host, port=port, clone_user=clone_user, clone_password=clone_password,
                             max_mem=max_mem, cores=cores, name=name, daemon=daemon)

        # 添加 build slave 相关的参数
        logger = self.logger.getChild("__init__")
        self.replication_user = replication_user
        self.replication_password = replication_password

        logger.debug(
            f"init MySQLBuildSlave instance replication_user = '{self.replication_user}'  replication_password='{self.replication_password}' ")

    def build_slave(self):
        """
        自动创建 slave
        """
        logger = self.logger.getChild('build_slave')
        # 第一步、执行远程克隆
        self.remote_clone()

        # 第二步、检查远程克隆是否成功完成
        if not self.is_successful_complete == True:

            # 远程克隆没有成功完成
            logger.error("remote clone fail can't rebuid slave")
            return

        # 如果可以执行到这里说明，远程克隆成功了
        # 可以进入到配置 slave 阶段了
        self.is_successful_complete = False

        wait_counter = 90
        for _ in range(wait_counter):
            if checkings.is_port_in_use(ip="127.0.0.1", port=self.port):
                # 如果 MySQL 已经监听在了 self.port 也要等 11 秒之后再执行连接
                logger.info("wait mysql protocol avaiable")
                time.sleep(11)
                break

            logger.warning(f"wait mysqld-{self.port} avariable")
            time.sleep(1)
        else:
            logger.error(
                f"mysqld-{self.port} not avariable concat your dba for help")

        # 第三步、执行 change master to & start slave

        cnx = None
        try:
            logger.debug(
                f"connect to mysqld-{self.port} with user={self.replication_user} password={self.replication_password}")
            cnx = connector.connect(host="127.0.0.1", port=self.port,
                                    user=self.replication_user, password=self.replication_password)
            cursor = cnx.cursor()
            change_sql = f"change master to master_host='{self.host}',master_port={self.port},master_user='{self.replication_user}',master_password='{self.replication_password}',master_ssl = 1,master_auto_position=1;"

            # 准备执行 change master to
            logger.info(f"prepare execute '{change_sql}'")
            cursor.execute(change_sql)

            # 准备执行 start slave

            start_sql = "start slave;"
            logger.info(f"prepare execute '{start_sql}' ")
            cursor.execute(start_sql)

            self.is_successful_complete = True

        except Exception as err:
            logger.error(f"config replication slave got error {err}")

        finally:
            if hasattr(cnx, 'close'):
                cnx.close()

        logger.info("rebuild mysql slave complete")

    def run(self):
        """
        """
        self.build_slave()


class MySQLBuildMGR(MySQLCloner):
    """
    实现 MySQL-MGR 的自动化安装与配置
    """
    logger = logger.getChild("MySQLBuildMGR")

    def __init__(self, pkg="mysql-8.0.18-linux-glibc2.12-x86_64.tar.xz",
                 port=3306, members="127.0.0.1,127.0.0.2,127.0.0.3", max_mem=128, cores=1,
                 clone_password='dbma@0352', repl_password='dbma@0352', name='imgr', daemon=True):
        """
        MGR 环境的安装与配置

        attrs:
            self.port
            self.group_seeds
            self.local_address
            self.is_primary_node
            self.member_ip_list
            self.is_mgr = True
            self.is_successful_complete = False

        """
        logger = self.logger.getChild("__init__")

        # 抽取出 primary 结点的 IP 地址
        # host = 主结点的 IP 地址
        host, *_ = members.split(',')
        clone_user = "cloneuser"
        self.port = port
        self.is_mgr = True
        self.is_successful_complete = False
        self.clone_password = clone_password
        self.repl_password = repl_password

        logger.info(f"using {host}:{port} as primary node")

        MySQLCloner.__init__(self, pkg=pkg, host=host, port=port, clone_user=clone_user, clone_password=clone_password,
                             max_mem=max_mem, cores=cores, name=name, daemon=daemon)

        logger.debug(
            f"create {self.__class__.__name__} instance using pkg='{pkg}' port='{port}' members='{members}' max_mem='{max_mem}' cores='{cores}'")

        logger.warning(
            f"clone user info user='{clone_user}' password='{clone_password}' ")

        # 配置 group_replication_group_seeds
        self.group_seeds = f":{port*10 + 1},".join(
            members.split(',')) + f":{port*10 + 1}"
        logger.info(f"group_replication_group_seeds = {self.group_seeds}")

        # 配置 group_replication_local_address
        # 把成员的 IP 列表转为集合
        member_ip_set = set()
        for ip in members.split(','):
            member_ip_set.add(ip)

        # 记录下所有成员的 IP 地址列表
        self.member_ip_list = [ip for ip in member_ip_set]

        # 查询出本机 IP 地址的集合
        local_ip_set = common.get_all_local_ip()
        local_ip = (local_ip_set & member_ip_set).pop()
        self.local_address = f"{local_ip}:{port * 10 + 1}"
        logger.info(f"group_replication_local_address = {self.local_address}")

        self.is_primary_node = host in local_ip_set

        logger.info(f"current node is primary node? = {self.is_primary_node}")

    def _mgr_checks(self):
        """
        检查要安装 MGR 要满足的要求
        @NotSupportedMySQLVersionError
        @PortIsInUseError
        @UserAlreadyExistsError
        @FileAlreadyExistsError
        @DirecotryAlreadyExistsError
        @FileNotExistsError
        """
        logger = self.logger.getChild('_mgr_checks')

        try:
            MySQLInstallerMixin._basic_checks(self)
        except Exception as err:
            raise err

        # 如果可以执行到这里说明基本的安装检查项通过了
        # 检查 mgr 同步用的端口是否被占用
        if checkings.is_port_in_use(ip="127.0.0.1", port=self.port * 10 + 1):
            logger.error(f"MGR port {self.port * 10 + 1} is in use ")
            raise errors.PortIsInUseError(
                f"MGR port {self.port * 10 + 1} is in use ")

        # 检查主机间的 DNS 是否
        for member_ip in self.member_ip_list:

            # 检查每一个结点的 IP 地址，验证 DNS 是否已经被配置
            try:
                socket.gethostbyaddr(member_ip)
            except Exception as err:
                logger.error(f"can't get host-name by ip '{member_ip}' ")
                # 退出循环,并标记当前的环境并没有 DNS 相关的配置
                __is_dns_configed = False
                break
        else:
            # 没有执行 break 说明 DNS 是有配置的
            return

        # 可以执行到这里说明 DNS 没有配置
        # 如果当前的环境并没有配置好 DNS 就在这里给它配置一下
        with common.sudo("config dns for mgr"):

            for member_ip in self.member_ip_list:

                # 配置主机名
                # dbm-127-0-0-1
                hostname = "dbm-{}".format(member_ip.split('.', '-'))
                subprocess.run(
                    f"hostnamectl set-hostname {hostname} ", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                # 配置 /etc/hosts
                line = f"{member_ip}    {hostname}"
                with open("/etc/hosts", 'a') as f_host:
                    f_host.write(f'\n{line}\n')

    def build_primary(self):
        """
        安装配置 MGR 的 primary 结点
        """
        logger = self.logger.getChild("build_primary")
        try:

            # 检查 是否满足 MGR 相关的配置
            # 如果是 DNS 的问题 _mgr_check 会自动配置
            self._mgr_checks()
        except Exception as err:
            logger.error("build MGR primary node faild")
            return

        # 开始安装 primary 结点
        # 因为 self.is_mgr == True 所以 install 会自动配置 MGR 的内容
        self.install()

        # 安装完成之后要等待启动完成
        wait_counter = 30
        for _ in range(wait_counter):
            if checkings.is_port_in_use(ip="127.0.0.1", port=self.port):

                #
                logger.info("mysql protocol avriable")
                break

            logger.info("wait 1 seconds for mysql protocol avriable")
            time.sleep(1)

        # 强制 sleep 7 秒
        time.sleep(7)

        # 启动 MGR
        cnx = None
        try:

            # 连接到已经安装好的 primary 结点
            logger.info(
                f"connector to primary node(127.0.0.1:{self.port}) user='dbma' password='{cnf.init_pwd}' ")

            cnx = connector.connect(
                host="127.0.0.1", port=self.port, user="dbma", password=cnf.init_pwd)
            cursor = cnx.cursor()
            # 直接一步到位有可能会创建 primary 失败(未知的原因)
            #mgr_sql = "set @@global.group_replication_bootstrap_group=ON;start group_replication;set @@global.group_replication_bootstrap_group=OFF;"
            # 打印出 primary 结点上执行的语句

            # 第一步：打开开关
            sql = "set @@global.group_replication_bootstrap_group=ON;"
            logger.info(sql)
            cursor.execute(sql)

            # 第二步：启动 MGR
            sql = "start group_replication;"
            logger.info(sql)
            cursor.execute(sql)

            # 第三步：关闭开关
            sql = "set @@global.group_replication_bootstrap_group=OFF;"
            logger.info(sql)
            cursor.execute(sql)

        except Exception as err:

            # 配置 primary 结点遇到了异常
            logger.error(f"{err}")
        finally:

            # close
            if hasattr(cnx, 'close'):
                cnx.close()

        self.is_successful_complete = True

        logger.info("build MGR primary node complete")

    def build_seconder(self):
        """
        安装配置 seconder 结点
        """

        logger = self.logger.getChild("build_seconder")
        try:
            # 检查 是否满足 MGR 相关的配置
            # 如果是 DNS 的问题 _mgr_check 会自动配置
            self._mgr_checks()
        except Exception as err:
            logger.error("build MGR primary node faild")
            return

        # 直接克隆一个实例
        self.remote_clone()

        if not self.is_successful_complete == True:

            # 远程克隆没有成功完成
            logger.error("remote clone fail can't rebuid slave")
            return

        logger.info('wait mysql restart complete ...')
        wait_counter = 90
        for _ in range(wait_counter):

            #
            if checkings.is_port_in_use(ip="127.0.0.1", port=self.port):
                time.sleep(11)
                break
            logger.debug("wait 1 seconds for mysql protoco available")
            time.sleep(1)
        else:

            # 没有被 break
            logger.error(
                "after remote clone mysql restart fail ,concat your dba for help")
            logger.error("build MGR seconder fail")
            return

        # 配置 seconder 节点
        cnx = None
        try:
            logger.debug(
                f"connect to 127.0.0.1:{self.port} user='repluser' password={self.repl_password} ")
            cnx = connector.connect(
                host="127.0.0.1", port=self.port, user="repluser", password=self.repl_password)
            cursor = cnx.cursor()
            change_sql = f"change master to master_user='repluser',master_password='{self.repl_password}' for channel 'group_replication_recovery';"
            logger.info(change_sql)
            cursor.execute(change_sql)
            mgr_sql = "start group_replication;"
            # 打印出 seconder 结点上执行的语句
            logger.info(mgr_sql)
            cursor.execute(mgr_sql)
        except Exception as err:
            self.is_successful_complete = True
            logger.error(f"{err}")
        finally:
            if hasattr(cnx, 'close'):
                cnx.close()

        if self.is_successful_complete == False:

            # 说明 remote clone 没有成功
            logger.error("build MGR seconder node fail")
            return

        logger.info("build MGR seconder node complete")

    def run(self):
        """
        """
        if self.is_primary_node == True:
            self.build_primary()
        else:
            self.build_seconder()


class MySQLShellInstaller(threading.Thread, MySQLShellInstallerMixin):
    """
    安装 MySQL-Shell
    """
    logger = logger.getChild("MySQLShellInstaller")

    def __init__(self, pkg="mysql-shell-8.0.18-linux-glibc2.12-x86-64bit.tar.gz"):
        """
        """
        logger = self.logger.getChild("__init__")
        threading.Thread.__init__(self, name="imshell", daemon=True)

        self.dbma = cnf
        self.pkg = pkg
        self.mysql_shell_basedir = os.path.join(
            self.dbma.mysql_install_dir, self.pkg.replace('.tar.gz', '').replace('.tar.xz', ''))
        self.mysql_shell_pkg_full_path = os.path.join(
            self.dbma.base_dir, 'pkg', self.pkg)
        self.is_successful_complete = False

    def run(self):
        """
        """
        self.install()
