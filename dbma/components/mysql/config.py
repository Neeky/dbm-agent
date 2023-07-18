# -*- coding: utf-8 -*-

"""MySQL 配置文件相关的逻辑

作者: 蒋乐兴|neeky@live.com
时间: 2023-03
"""

import re
import os
import json
import logging
import random
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from dbma.core import messages
from dbma.bil.fun import fname
from dbma.bil.osuser import MySQLUser
from dbma.core.configs import dbm_agent_config, Cnfr


@dataclass
class MySQLOptionsMixin(object):
    """
    定义所有 MySQL 配置项的键值对
    """

    # basic
    port: int = 3306
    basedir: str = None
    innodb_buffer_pool_size: str = None
    now: str = datetime.now().isoformat()

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
    binlog_transaction_dependency_tracking: str = "WRITESET"
    transaction_write_set_extraction: str = "XXHASH64"
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


@dataclass
class MySQLSRConfig(Cnfr, MySQLOptionsMixin):
    """
    实现 source / replica 架构的配置文件生成功能
    """

    # basic
    port: int = None
    basedir: str = None
    innodb_buffer_pool_size: str = None
    template: str = None

    def __post_init__(self):
        """
        根据传入的 port, basedir 计算出其它的属性
        """
        # 1 根据 port 识别出 user, 配置文件 ...
        self._init_ports()

        # 2 根据 basedir 识别出 version ....
        self._init_basedirs()

        # 3 根据 buffer pool 的值调整其它配置
        self._init_buffer_pools()

        # 4 设置其它非依赖项
        self._init_others()

    def _init_ports(self):
        """
        设置那些当我们知道 port 就能抢断出来的配置项, 在这里统一完成设置
        """
        # 用户名
        self.user = MySQLUser(self.port).name

        # 数据目录+binlog目录
        self.datadir = os.path.join(
            dbm_agent_config.mysql_datadir_parent, str(self.port)
        )
        self.log_bin = os.path.join(
            dbm_agent_config.mysql_binlogdir_parent, str(self.port) + "/binlog"
        )

        # 管理端口+ mysqlx 端口
        self.admin_port = self.port * 10 + 2
        self.mysqlx_port = self.port * 10

        # socket 文件 + pid 文件的位置
        self.socket = os.path.join(self.datadir, "mysql.sock")
        self.mysqlx_socket = os.path.join(self.datadir, "mysqlx.sock")
        self.pid_file = os.path.join(self.datadir, "mysql.pid")

        # 配置文件的全路径
        self.config_file_path = "/etc/my-{}.cnf".format(self.port)

    def _init_basedirs(self):
        """
        由于每一个版本的配置文件都有差别，dbm-agent 为 mysql 的每一个小版本都提供了配置文件，
        所以这里就要根据版本号来确认要执行哪个配置文件模板。

        """
        p = re.compile("mysql-(?P<version>\d{1}.\d{1}.\d{1,2})")
        # 根据 basedir 识别出版本号
        self.version = p.search(str(self.basedir)).group("version")
        # 根据版本号识别出模板文件
        self.template = "mysql-{}.cnf.jinja".format(self.version)

    def _init_others(self):
        """
        计算其它属性值
        """
        # 随机生成一个 server-id
        self.server_id = random.randint(1024, 8192)

    def _init_buffer_pools(self):
        """
        根据给定的 buffer_pool 的大小，调整 buffer pool 的配置， log_buffer 的配置
        """
        if self.innodb_buffer_pool_size.endswith("M"):
            # M 级别
            self.innodb_buffer_pool_instances = 1
            self.innodb_log_buffer_size = "64M"
        elif self.innodb_buffer_pool_size.endswith("G"):
            # G 级别
            size = re.match(r"\d*", self.innodb_buffer_pool_size).group(0)
            size = int(size)
            if size <= 2:
                self.innodb_buffer_pool_instances = 1
                self.innodb_log_buffer_size = "64M"
            elif size <= 4:
                self.innodb_buffer_pool_instances = 2
                self.innodb_log_buffer_size = "128M"
            elif size <= 8:
                self.innodb_buffer_pool_instances = 4
                self.innodb_log_buffer_size = "256M"
            elif size <= 16:
                self.innodb_buffer_pool_instances = 8
                self.innodb_log_buffer_size = "512M"
            else:
                self.innodb_buffer_pool_instances = 16
                self.innodb_log_buffer_size = "1G"

    def save_init_cnf(self):
        """
        生成 MySQL 初始化传用的配置文件
        """
        # 1. 保留现场
        _config = self.config_file_path
        _template = self.template

        # 2. init-cnf 专用的配置
        self.config_file_path = dbm_agent_config.mysql_init_cnf
        self.template = (
            "mysql-8.0-init-only.jinja"
            if self.version.startswith("8.0")
            else "mysql-5.7-init-only.jinja"
        )
        self.save()

        # 4. init-user 专用的配置
        self.config_file_path = dbm_agent_config.mysql_init_user_sql_file
        self.template = (
            "init-8.0.x.sql" if self.version.startswith("8.0") else "init-5.7.x.sql"
        )
        self.save()

        # 还原现场
        self.config_file_path = _config
        self.template = _template


@dataclass
class MySQLMGRConfig(Cnfr, MySQLOptionsMixin):
    """
    实现 MySQL-MGR 架构的配置文件生成功能
    """

    pass


@dataclass
class MySQLSystemdConfig(Cnfr):
    port: int = 3306
    basedir: str = None

    # 以下为自动参数
    user: str = None
    template: str = "mysqld.service.jinja"

    def __post_init__(self):
        """ """
        self.user = MySQLUser(self.port).name
        self.config_file_path = Path(
            "/usr/lib/systemd/system/mysqld-{}.service".format(self.port)
        )
