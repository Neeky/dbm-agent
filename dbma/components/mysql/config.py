# -*- encoding: utf-8 -*-

"""MySQL 配置文件相关的逻辑

作者: 蒋乐兴|neeky@live.com
时间: 2023-03
"""

import re
import os
import json
import logging
import random
from enum import Enum
from pathlib import Path
from jinja2 import Template
from dataclasses import dataclass, asdict
from dbma.core import messages
from dbma.bil.fun import fname
from dbma.core.configs import dbm_agent_config
from dbma.components.mysql.exceptions import MySQLTemplateFileNotExistsException


class MySQLTemplateTypes(Enum):
    """定义配置文件模板类型"""

    # MySQL 配置文件
    MYSQL_CONFIG_FILE = 1

    # MySQL init 专用配置文件
    MYSQL_INIT_CONFIG_FILE = 2

    # MySQL systemd 配置文件
    MYSQL_SYSTEMD_FILE = 3


@dataclass
class MySQLConfig(object):
    """MySQL 配置文件的动态生成"""

    # basic
    basedir: str = None
    port: str = None
    innodb_buffer_pool_size: str = None

    # region global-config
    version: str = None
    user: str = None
    datadir: str = None
    server_id: int = None
    bind_address: str = "*"
    admin_address: str = "127.0.0.1"
    admin_port: str = None
    mysqlx_port: str = None
    socket: str = None
    mysqlx_socket: str = None
    pid_file: str = None
    character_set_server: str = "utf8mb4"
    collation_server: str = "utf8mb4_0900_ai_ci"
    collation_database: str = "utf8mb4_0900_ai_ci"
    open_files_limit: int = 102400
    max_prepared_stmt_count: int = 4194304
    skip_name_resolve: str = "ON"
    super_read_only: str = "ON"
    read_only: str = "ON"
    log_timestamps: str = "SYSTEM"
    event_scheduler: str = "ON"
    auto_generate_certs: str = "ON"
    activate_all_roles_on_login: str = "OFF"
    end_markers_in_json: str = "OFF"
    tmpdir: str = "/tmp/"
    max_connections: int = 4096
    thread_cache_size: int = 32
    autocommit: str = "ON"
    sort_buffer_size: int = 262144
    join_buffer_size: int = 262144
    eq_range_index_dive_limit: int = 200
    authentication_policy: str = "*,,"
    show_gipk_in_create_table_and_information_schema: str = "ON"
    sql_generate_invisible_primary_key: str = "ON"

    # endregion global-config

    # region for-tables
    big_tables: str = "ON"
    sql_require_primary_key: str = "ON"
    lower_case_table_names: int = 1
    auto_increment_increment: int = 1
    auto_increment_offset: int = 1
    table_open_cache: int = 10240
    table_definition_cache: int = 2048
    table_open_cache_instances: int = 8
    # endregion for-tables

    # region for-nets
    max_allowed_packet: str = "1G"
    connect_timeout: int = 10
    interactive_timeout: int = 28800
    net_read_timeout: int = 30
    net_retry_count: int = 10
    net_write_timeout: int = 60
    net_buffer_length: int = 32768
    # endregion for-nets

    # region general-logs
    log_output: str = "FILE"
    general_log: str = "OFF"
    general_log_file: str = "general.log"
    # endregion general-logs

    # region slow-logs
    slow_query_log: str = "ON"
    slow_query_log_file: str = "slow.log"
    long_query_time: str = 1
    log_queries_not_using_indexes: str = "OFF"
    log_slow_admin_statements: str = "ON"
    log_slow_replica_statements: str = "ON"
    log_slow_slave_statements: str = "ON"
    # endregion slow-logs

    # region error-logs
    log_error: str = "err.log"
    log_statements_unsafe_for_binlog: str = "ON"
    # endregion error-logs

    # region binlogs
    log_bin: str = None
    binlog_checksum: str = "CRC32"
    log_bin_trust_function_creators: str = "ON"
    binlog_direct_non_transactional_updates: str = "OFF"
    expire_logs_days: int = 7
    binlog_expire_logs_seconds: int = 2592000
    binlog_error_action: str = "ABORT_SERVER"
    binlog_format: str = "ROW"
    max_binlog_stmt_cache_size: int = 18446744073709547520
    max_binlog_cache_size: int = 18446744073709547520
    max_binlog_size: str = "1GB"
    binlog_order_commits: str = "ON"
    binlog_row_image: str = "FULL"
    binlog_row_metadata: str = "FULL"
    binlog_rows_query_log_events: str = "ON"
    binlog_stmt_cache_size: int = 32768
    log_replica_updates: str = "ON"
    binlog_transaction_compression: str = "ON"
    binlog_transaction_dependency_history_size: int = 25000
    binlog_transaction_dependency_tracking: str = "COMMIT_ORDER"
    sync_binlog: int = 1
    binlog_cache_size: int = 32768
    binlog_group_commit_sync_delay: int = 0
    binlog_group_commit_sync_no_delay_count: int = 0
    # endregion binlogs

    # region gtids
    gtid_mode: str = "ON"
    binlog_gtid_simple_recovery: str = "ON"
    enforce_gtid_consistency: str = "ON"
    gtid_executed_compression_period: int = 0
    # endregion gtids

    # region clone
    plugin_load_add: str = "mysql_clone.so"
    clone_autotune_concurrency: str = "ON"
    clone_buffer_size: str = "16M"
    clone_block_ddl: str = "OFF"
    clone_delay_after_data_drop: int = 300
    clone_ddl_timeout: int = 300
    clone_donor_timeout_after_network_failure: int = 5
    clone_enable_compression: str = "ON"
    clone_max_concurrency: int = 16
    clone_max_data_bandwidth: int = 0
    clone_max_network_bandwidth: int = 0
    clone_valid_donor_list: str = "NULL"
    # endregion clone

    # region replication
    rpl_semi_sync_master_enabled: str = "ON"
    rpl_semi_sync_slave_enabled: str = "ON"
    rpl_semi_sync_master_timeout: int = 1000
    rpl_semi_sync_master_wait_point: str = "AFTER_SYNC"
    rpl_semi_sync_master_wait_no_slave: str = "ON"
    rpl_semi_sync_master_wait_for_slave_count: int = 1
    sync_source_info: int = 10000
    skip_slave_start: str = "ON"
    skip_replica_start: str = "ON"
    log_slave_updates: str = "ON"
    replica_load_tmpdir: str = "/tmp/"
    master_info_repository: str = "table"
    relay_log_info_repository: str = "table"
    plugin_load_add: str = "semisync_master.so"
    plugin_load_add: str = "semisync_slave.so"
    relay_log: str = "relay-bin"
    sync_relay_log: int = 10000
    sync_relay_log_info: int = 10000
    slave_preserve_commit_order: str = "ON"
    replica_preserve_commit_order: str = "ON"
    slave_parallel_type: str = "LOGICAL_CLOCK"
    replica_parallel_type: str = "LOGICAL_CLOCK"
    slave_parallel_workers: int = 4
    replica_parallel_workers: int = 4
    replica_max_allowed_packet: str = "1G"
    transaction_write_set_extraction: str = "XXHASH64"
    # endregion replication

    # region engines
    default_storage_engine: str = "InnoDB"
    default_tmp_storage_engine: str = "InnoDB"
    internal_tmp_mem_storage_engine: str = "TempTable"
    # endregion engines

    # region innodbs
    innodb_data_home_dir: str = "./"
    innodb_data_file_path: str = "ibdata1:64M:autoextend"
    innodb_page_size: int = 16384
    innodb_default_row_format: str = "DYNAMIC"
    innodb_log_group_home_dir: str = "redo-files"
    innodb_redo_log_capacity: str = "1G"
    innodb_redo_log_encrypt: str = "OFF"
    innodb_online_alter_log_max_size: str = "256M"
    innodb_undo_directory: str = "undo-files"
    innodb_undo_log_encrypt: str = "OFF"
    innodb_undo_log_truncate: str = "ON"
    innodb_max_undo_log_size: str = "1G"
    innodb_rollback_on_timeout: str = "OFF"
    innodb_rollback_segments: int = 128
    innodb_log_checksums: str = "ON"
    innodb_checksum_algorithm: str = "crc32"
    innodb_log_compressed_pages: str = "ON"
    innodb_doublewrite: str = "ON"
    innodb_doublewrite_dir: str = "dblwr-files"
    innodb_doublewrite_files: int = 4
    innodb_doublewrite_batch_size: int = 0
    innodb_commit_concurrency: int = 0
    innodb_read_only: str = "OFF"
    innodb_dedicated_server: str = "OFF"
    innodb_old_blocks_pct: int = 37
    innodb_old_blocks_time: int = 1000
    innodb_random_read_ahead: str = "OFF"
    innodb_read_ahead_threshold: int = 56
    innodb_max_dirty_pages_pct_lwm: int = 10
    innodb_max_dirty_pages_pct: int = 90
    innodb_lru_scan_depth: str = 1024
    innodb_adaptive_flushing: str = "ON"
    innodb_adaptive_flushing_lwm: int = 10
    innodb_flushing_avg_loops: int = 30
    innodb_buffer_pool_dump_pct: int = 25
    innodb_buffer_pool_dump_at_shutdown: str = "ON"
    innodb_buffer_pool_load_at_startup: str = "ON"
    innodb_buffer_pool_filename: str = "ib_buffer_pool"
    innodb_stats_persistent: str = "ON"
    innodb_stats_on_metadata: str = "OFF"
    innodb_stats_method: str = "nulls_equal"
    innodb_stats_auto_recalc: str = "ON"
    innodb_stats_include_delete_marked: str = "OFF"
    innodb_stats_persistent_sample_pages: int = 20
    innodb_stats_transient_sample_pages: int = 8
    innodb_status_output: str = "OFF"
    innodb_status_output_locks: str = "OFF"
    innodb_buffer_pool_dump_now: str = "OFF"
    innodb_buffer_pool_load_abort: str = "OFF"
    innodb_buffer_pool_load_now: str = "OFF"
    innodb_thread_concurrency: int = 0
    innodb_concurrency_tickets: int = 5000
    innodb_thread_sleep_delay: int = 10000
    innodb_adaptive_max_sleep_delay: int = 150000
    innodb_read_io_threads: int = 4
    innodb_write_io_threads: int = 4
    innodb_use_native_aio: str = "ON"
    innodb_flush_sync: str = "ON"
    innodb_spin_wait_delay: int = 6
    innodb_purge_threads: int = 4
    innodb_purge_batch_size: int = 300
    innodb_purge_rseg_truncate_frequency: int = 128
    innodb_deadlock_detect: str = "ON"
    innodb_print_all_deadlocks: str = "OFF"
    innodb_lock_wait_timeout: int = 50
    innodb_table_locks: str = "ON"
    innodb_sync_array_size: int = 1
    innodb_sync_spin_loops: int = 30
    innodb_print_ddl_logs: str = "OFF"
    innodb_replication_delay: int = 0
    innodb_cmp_per_index_enabled: str = "OFF"
    innodb_disable_sort_file_cache: str = "OFF"
    innodb_numa_interleave: str = "OFF"
    innodb_strict_mode: str = "ON"
    innodb_sort_buffer_size: int = 1048576
    innodb_fast_shutdown: int = 0
    innodb_force_load_corrupted: str = "OFF"
    innodb_force_recovery: str = 0
    innodb_temp_tablespaces_dir: str = "innodb-temp-tablespaces"
    innodb_tmpdir: str = "innodb-temps"
    innodb_temp_data_file_path: str = "ibtmp1:12M:autoextend"
    innodb_page_cleaners: int = 4
    innodb_adaptive_hash_index: str = "OFF"
    innodb_adaptive_hash_index_parts: int = 8
    innodb_flush_log_at_timeout: int = 1
    innodb_fsync_threshold: int = 0
    innodb_fill_factor: int = 96
    innodb_file_per_table: str = "ON"
    innodb_autoextend_increment: int = 64
    innodb_open_files: int = 102400
    innodb_buffer_pool_chunk_size: str = "128M"
    innodb_flush_neighbors: int = 0
    innodb_io_capacity: int = 2000
    innodb_io_capacity_max: int = 20000
    innodb_autoinc_lock_mode: int = 2
    innodb_change_buffer_max_size: int = 25
    innodb_flush_method: str = "fsync"
    innodb_change_buffering: str = "ALL"
    innodb_flush_log_at_trx_commit: int = 1
    innodb_buffer_pool_instances: int = None
    innodb_log_buffer_size: str = None

    # expire
    innodb_log_files_in_group: int = 8
    innodb_log_file_size: str = "128M"
    # endregion innodbs

    # region ps
    performance_schema: str = "ON"
    # endregion ps

    def calcu_second_attrs(self):
        """根据已有的配置推导出相关的其它配置"""
        logging.info(messages.FUN_STARTS.format(fname()))

        self._calcu_deps_port()
        self._calcu_random_attrs()
        self._calcu_deps_mem()
        self._calcu_deps_basedir()

        logging.info(messages.FUN_ENDS.format(fname()))

    def save_to_target_dir(self, target_dir: Path = None):
        """以 json 格式保存到目标目录

        Parameters:
        -----------
        target_dir: Path
            json 格式配置文件要保存到的路径(parent-dir)
        """
        logging.info(messages.FUN_STARTS.format(fname()))

        # 检查参数
        if target_dir is None:
            # 没有给出 target_dir 就保存到 datadir
            json_file = Path(self.datadir) / "mysql-config.json"
        else:
            json_file = Path(target_dir) / "mysql-config.json"

        # 检查目录是否存在
        if not Path(target_dir).exists():
            logging.error(
                "dir '{}' not exists, skip save config to it .".format(target_dir)
            )
            logging.info(messages.FUN_ENDS.format(fname()))
            return

        # 保存到给定目录
        logging.info("write config file to '{}' .".format(json_file))
        json_data = asdict(self)
        with open(json_file, "w") as f:
            f.write(json.dumps(json_data, indent=4))

        logging.info(messages.FUN_ENDS.format(fname()))

    def find_mysql_template_file(self, mtt: MySQLTemplateTypes = None):
        """根据版本号加载配置文件模板，如果找不到对应的模板文件就返回 None

        Parameters:
        -----------
        mtt: MySQLTemplateTypes
            MySQL 配置文件模板类型

        Return:
        -------
        Path

        Exceptions:
        -----------
        MySQLTemplateFileNotExistsException

        """
        logging.info(messages.FUN_STARTS.format(fname()))

        # 根据需要的配置文件类型返回模板文件(Path)
        import dbma

        if mtt == MySQLTemplateTypes.MYSQL_CONFIG_FILE:
            template_file = Path(
                dbma.__file__
            ).parent / "static/cnfs/mysql-{}.cnf.jinja".format(self.version)
            # dbm-agent 只对 5.7.x 提供有限的支持、配置文件的模板最高为 5.7.25 、也就是说所有的版本都用这个一个模板
            if self.version.startswith("5.7"):
                template_file = Path(
                    dbma.__file__
                ).parent / "static/cnfs/mysql-{}.cnf.jinja".format("5.7.25")
                logging.info(
                    "5.7.xx version well using config template {}".format(template_file)
                )

        elif mtt == MySQLTemplateTypes.MYSQL_INIT_CONFIG_FILE:
            short_version = "8.0" if self.version.startswith("8.0") else "5.7"
            template_file = Path(
                dbma.__file__
            ).parent / "static/cnfs/mysql-{}-init-only.jinja".format(short_version)
        elif mtt == MySQLTemplateTypes.MYSQL_SYSTEMD_FILE:
            template_file = (
                Path(dbma.__file__).parent / "static/cnfs/mysqld.service.jinja"
            )
        logging.info("using template file {}".format(template_file))

        # 检查一下是否存在
        if template_file.exists():
            logging.info(messages.FUN_ENDS.format(fname()))
            return template_file

        logging.warning("template file '{}' not exists ".format(template_file))
        raise MySQLTemplateFileNotExistsException(template_file)

    def render_mysql_template(self, template: str = None):
        """渲染给定的 template 文件

        Parameters:
        -----------
        template: str
            模板文件的文字内容

        Return:
        -------
        str
            渲染之后的配置文件
        """
        logging.info(messages.FUN_STARTS.format(fname()))
        if template is None:
            logging.error("template is None .")
            return

        if not template.exists():
            logging.error("template not exists .")
            return

        with open(template, "r") as f:
            content = f.read()

        t = Template(content)
        logging.info(messages.FUN_ENDS.format(fname()))
        return t.render(asdict(self))

    def generate_cnf_config_file(self):
        """生成配置文件  /etc/my-{port}-cnf"""
        logging.info(messages.FUN_STARTS.format(fname()))
        # 根据版本号加载配置文件模板
        # 渲染模板
        # 保存渲染后的内容到文件
        try:
            tempate = self.find_mysql_template_file(
                MySQLTemplateTypes.MYSQL_CONFIG_FILE
            )
        except MySQLTemplateFileNotExistsException as err:
            logging.error("cannot generate cnf config file, becuase {}".format(err))
            raise err

        content = self.render_mysql_template(tempate)

        with open(Path("/etc/my-{}.cnf".format(self.port)), "w") as f:
            f.write(content)
        logging.info(messages.FUN_ENDS.format(fname()))

    def generate_init_cnf_config_file(self):
        """生成初始化专用文件, 用于解决 plugin-add 导致的一系列问题

        2023-03-29T11:25:08.320436+08:00 0 [Warning] [MY-013501] [Server] Ignoring --plugin-load[_add] list as the server is running with --initialize(-insecure).
        2023-03-29T11:25:09.326699+08:00 0 [ERROR] [MY-000067] [Server] unknown variable 'rpl_semi_sync_master_enabled=ON'.
        2023-03-29T11:25:09.326717+08:00 0 [ERROR] [MY-013236] [Server] The designated data directory /database/mysql/data/3306/ is unusable. You can remove all files that the server added to it.

        所以我们要在 init 的时候生成一份没有 plugin-add 的版本
        """
        logging.info("starts generate init cnf config file .")
        # 查询 mysql-init 的配置文件模板
        try:
            tempate = self.find_mysql_template_file(
                MySQLTemplateTypes.MYSQL_INIT_CONFIG_FILE
            )
        except MySQLTemplateFileNotExistsException as err:
            logging.error("cannot generate cnf config file, becuase {}".format(err))
            raise err

        content = self.render_mysql_template(tempate)

        with open(Path(dbm_agent_config.mysql_init_cnf), "w") as f:
            f.write(content)

        logging.info("starts generate init cnf config file .")

    def generate_systemd_cnf_config(self):
        """ """
        logging.info("starts generate systemd config file .")
        # 查询 mysql-init 的配置文件模板
        try:
            tempate = self.find_mysql_template_file(
                MySQLTemplateTypes.MYSQL_SYSTEMD_FILE
            )
        except MySQLTemplateFileNotExistsException as err:
            logging.error("cannot generate cnf config file, becuase {}".format(err))
            raise err

        content = self.render_mysql_template(tempate)

        with open(
            Path("/usr/lib/systemd/system/mysqld-{}.service".format(self.port)), "w"
        ) as f:
            f.write(content)

        logging.info("ends generate systemd config file .")

    def _calcu_deps_port(self):
        """计算依赖于 port 的配置项

        user = 'mysql' + str(port)
        """
        logging.info("starts _calcu_dep_port fun . ")
        # 设置参数
        # 目前 json 模块还不支持序列化 Path 对象，所以这里统一用 str 来表示路径
        self.user = dbm_agent_config.mysql_user_prefix + str(self.port)
        self.datadir = os.path.join(
            dbm_agent_config.mysql_datadir_parent, str(self.port)
        )
        self.admin_port = self.port * 10 + 2
        self.mysqlx_port = self.port * 10
        self.log_bin = os.path.join(
            dbm_agent_config.mysql_binlogdir_parent, str(self.port) + "/binlog"
        )

        # 跟据 datadir 计算 socket 文件的位置
        self.socket = os.path.join(self.datadir, "mysql.sock")
        self.mysqlx_socket = os.path.join(self.datadir, "mysqlx.sock")
        self.pid_file = os.path.join(self.datadir, "mysql.pid")

        logging.info("set user to {} .".format(self.user))
        logging.info("set datadir to {} .".format(self.datadir))
        logging.info("set admin_port to {} .".format(self.admin_port))
        logging.info("set mysqlx_port to {} .".format(self.mysqlx_port))
        logging.info("ends _calcu_dep_port fun . ")

    def _calcu_random_attrs(self):
        """生成随机值"""
        self.server_id = random.randint(1024, 8192)

    def _calcu_deps_mem(self):
        """计算内存相关的值"""
        if self.innodb_buffer_pool_size.endswith("M"):
            # M 级别
            self.innodb_buffer_pool_instances = 1
            self.innodb_log_buffer_size = "64M"
        elif self.innodb_buffer_pool_size.endswith("G"):
            # G 级别
            size = re.match("\d*", self.innodb_buffer_pool_size).group(0)
            size = int(size)
            if size <= 2:
                self.innodb_buffer_pool_instances = 1
                self.innodb_log_buffer_size = "64M"
            elif size <= 4:
                self.innodb_buffer_pool_instances = size
                self.innodb_log_buffer_size = "128M"
            elif size <= 8:
                self.innodb_buffer_pool_instances = size
                self.innodb_log_buffer_size = "256M"
            elif size <= 16:
                self.innodb_buffer_pool_instances = size
                self.innodb_log_buffer_size = "512M"
            else:
                self.innodb_buffer_pool_instances = 16
                self.innodb_log_buffer_size = "1G"

    def _calcu_deps_basedir(self):
        """根据 basedir 计算出 MySQL 的 version"""
        m = re.search(r"mysql-(?P<version>\d{1}.\d{1,2}.\d{1,2})-linux", self.basedir)
        self.version = m.group("version")
