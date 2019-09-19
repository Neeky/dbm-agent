"""
读取模板并渲染
"""
# (c) 2019, LeXing Jinag <neeky@live.com 1721900707@qq.com https://www.sqlpy.com/> 
# Copyright: (c) 2019, dbm Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import copy
import random
import logging
from jinja2 import Environment,FileSystemLoader
from . import errors
from . import checkings
from . import common
from . import gather

logger = logging.getLogger('dbm-agent').getChild(__name__)


class BaseRender(object):
    """
    所有配置文件渲染功能的基类
    """
    def __init__(self,tmpl_dir:str="/usr/local/dbm-agent/etc/templates/",
                      tmpl_file:str="mysql-8.0.17.cnf.jinja"):
        logger.info(f"load template from {tmpl_dir}")
        logger.info(f"template file name {tmpl_file}")
        if not checkings.is_directory_exists(tmpl_dir):
            logger.warning(f"directory {tmpl_dir} not exists")
            raise errors.DirectoryNotExistsError(f"{tmpl_dir}")

        if not checkings.is_file_exists(os.path.join(tmpl_dir,tmpl_file)):
            logger.warning(f"template file {tmpl_file} not exists")
            raise errors.FileNotExistsError(f"{os.path.join(tmpl_dir,tmpl_file)}")

        env = Environment(loader=FileSystemLoader(searchpath=tmpl_dir))
        tmpl = env.get_template(tmpl_file)

        self.tmpl = tmpl

    def render(self)->str:
        raise NotImplementedError()


class MysqlRender(BaseRender):
    """
    """
    defaults = {
        # basic
        'user': None,
        'port': None,
        'basedir': None,
        'datadir': None,
        'socket': None,
        'pid': None,
    }

    def __init__(self,pkg:str="mysql-8.0.17-linux-glibc2.12-x86_64.tar.xz",port:int=3306,max_mem:int=1024,
                 tmpl_dir:str="/usr/local/dbm-agent/etc/templates/",tmpl_file="mysql-8.0.17.cnf.jinja",cores=1):
        super().__init__(tmpl_dir=tmpl_dir,tmpl_file=tmpl_file)

        #
        logger.info(f"mysql pkg {pkg} max memory {max_mem}")
        self.defaults = copy.deepcopy(MysqlRender.defaults)
        self.pkg = pkg
        self.max_mem = max_mem
        self.cores = cores

        # basic
        self.user = f"mysql{port}"
        self.port = port
        self.mysqlx_port = port * 10
        self.admin_port = port * 10 + 2
        self.admin_address = '127.0.0.1'
        self.basedir = os.path.join('/usr/local/',pkg.replace('.tar.gz','').replace('.tar.xz',''))
        self.datadir = os.path.join(f'/database/mysql/data/{port}')
        self.socket = f"/tmp/mysql-{port}.sock"
        self.mysqlx_socket = f"/tmp/mysqlx-{self.mysqlx_port}.sock"
        self.pid_file = f"/tmp/mysql-{port}.pid"
        self.server_id = random.randint(1,4097)
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
        self.log_bin = 'mysql-bin'
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
        self.sync_relay_log = 10000
        self.sync_relay_log_info = 10000
        self.rpl_semi_sync_slave_enabled = 1

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
        self.innodb_flush_log_at_timeout =1
        self.innodb_flush_log_at_trx_commit = 1
        self.innodb_flush_method = 'O_DIRECT'
        self.innodb_fsync_threshold = 0
        self.innodb_change_buffer_max_size = 25
        self.innodb_change_buffering  = 'all'
        self.innodb_fill_factor = 90
        self.innodb_file_per_table = 'ON'
        self.innodb_autoextend_increment = 64
        self.innodb_open_files = 100000


        self.defaults.update({
            'user': self.user,
            'port': self.port,
            'mysqlx_port': self.mysqlx_port,
            'admin_address': self.admin_address,
            'admin_port': self.admin_port,
            'basedir': self.basedir,
            'datadir': self.datadir,
            'socket': self.socket,
            'mysqlx_socket': self.mysqlx_socket,
            'pid_file': self.pid_file,
            'server_id': self.server_id,
            'open_files_limit': self.open_files_limit,
            'max_prepared_stmt_count': self.max_prepared_stmt_count,
            'skip_name_resolve': self.skip_name_resolve,
            'super_read_only': self.super_read_only,
            'log_error': self.log_error,
            'sql_require_primary_key': self.sql_require_primary_key,
            'log_timestamps': self.log_timestamps,
            'lower_case_table_names': self.lower_case_table_names,
            'auto_increment_increment': self.auto_increment_increment,
            'auto_increment_offset': self.auto_increment_offset,
            'event_scheduler': self.event_scheduler,
            'auto_generate_certs': self.auto_generate_certs,
            'big_tables': self.big_tables,
            'join_buffer_size': self.join_buffer_size,
            'activate_all_roles_on_login': self.activate_all_roles_on_login,
            'end_markers_in_json': self.end_markers_in_json,
            'tmpdir': self.tmpdir,
            'max_connections': self.max_connections,
            'autocommit': self.autocommit,
            'sort_buffer_size': self.sort_buffer_size,
            'eq_range_index_dive_limit': self.eq_range_index_dive_limit,
            #
            'table_open_cache': self.table_open_cache,
            'table_definition_cache': self.table_definition_cache,
            'table_open_cache_instances': self.table_open_cache_instances,
            'max_allowed_packet': self.max_allowed_packet,
            'bind_address': self.bind_address,
            'connect_timeout': self.connect_timeout,
            'interactive_timeout': self.interactive_timeout,
            'net_read_timeout': self.net_read_timeout,
            'net_retry_count': self.net_retry_count,
            'net_write_timeout': self.net_write_timeout,
            'net_buffer_length': self.net_buffer_length,
            'log_output': self.log_output,
            'general_log': self.general_log,
            'general_log_file': self.general_log_file,
            'log_statements_unsafe_for_binlog': self.log_statements_unsafe_for_binlog,
            'long_query_time': self.long_query_time,
            'log_queries_not_using_indexes': self.log_queries_not_using_indexes,
            'log_slow_admin_statements': self.log_slow_admin_statements,
            'log_slow_slave_statements': self.log_slow_slave_statements,
            'slow_query_log': self.slow_query_log,
            'slow_query_log_file': self.slow_query_log_file,
            'log_bin': self.log_bin,
            'binlog_checksum': self.binlog_checksum,
            'log_bin_trust_function_creators': self.log_bin_trust_function_creators,
            'binlog_direct_non_transactional_updates': self.binlog_direct_non_transactional_updates,
            'binlog_expire_logs_seconds': self.binlog_expire_logs_seconds,
            'binlog_error_action': self.binlog_error_action,
            'binlog_format': self.binlog_format,
            'max_binlog_stmt_cache_size': self.max_binlog_stmt_cache_size,
            'max_binlog_cache_size': self.max_binlog_cache_size,
            'max_binlog_size': self.max_binlog_size,
            'binlog_order_commits': self.binlog_order_commits,
            'binlog_row_image': self.binlog_row_image,
            'binlog_row_metadata': self.binlog_row_metadata,
            'binlog_rows_query_log_events': self.binlog_rows_query_log_events,
            'sync_binlog': self.sync_binlog,
            'binlog_stmt_cache_size': self.binlog_stmt_cache_size,
            'log_slave_updates': self.log_slave_updates,
            'binlog_group_commit_sync_delay': self.binlog_group_commit_sync_delay,
            'binlog_group_commit_sync_no_delay_count': self.binlog_group_commit_sync_no_delay_count,
            'binlog_cache_size': self.binlog_cache_size,
            'binlog_transaction_dependency_history_size': self.binlog_transaction_dependency_history_size,
            'binlog_transaction_dependency_tracking': self.binlog_transaction_dependency_tracking,
            'master_info_repository': self.master_info_repository,
            'sync_master_info': self.sync_master_info,
            'rpl_semi_sync_master_timeout': self.rpl_semi_sync_master_timeout,
            'rpl_semi_sync_master_enabled': self.rpl_semi_sync_master_enabled,
            'relay_log_info_repository': self.relay_log_info_repository,
            'skip_slave_start': self.skip_slave_start,
            'slave_parallel_type': self.slave_parallel_type,
            'slave_parallel_workers': self.slave_parallel_workers,
            'slave_max_allowed_packet': self.slave_max_allowed_packet,
            'slave_load_tmpdir': self.slave_load_tmpdir,
            'sync_relay_log': self.sync_relay_log,
            'sync_relay_log_info': self.sync_relay_log_info,
            'rpl_semi_sync_slave_enabled': self.rpl_semi_sync_slave_enabled,
            'binlog_gtid_simple_recovery': self.binlog_gtid_simple_recovery,
            'enforce_gtid_consistency': self.enforce_gtid_consistency,
            'gtid_executed_compression_period': self.gtid_executed_compression_period,
            'gtid_mode': self.gtid_mode,

            # engiens
            'default_storage_engine': self.default_storage_engine,
            'default_tmp_storage_engine': self.default_tmp_storage_engine,
            'internal_tmp_mem_storage_engine': self.internal_tmp_mem_storage_engine,

            # innodb
            'innodb_data_home_dir': self.innodb_data_home_dir,
            'innodb_data_file_path': self.innodb_data_file_path,
            'innodb_page_size': self.innodb_page_size,
            'innodb_default_row_format': self.innodb_default_row_format,
            'innodb_log_group_home_dir': self.innodb_log_group_home_dir,
            'innodb_log_files_in_group': self.innodb_log_files_in_group,
            'innodb_log_file_size': self.innodb_log_file_size,
            'innodb_log_buffer_size': self.innodb_log_buffer_size,
            'innodb_redo_log_encrypt': self.innodb_redo_log_encrypt,
            'innodb_online_alter_log_max_size': self.innodb_online_alter_log_max_size,
            'innodb_undo_directory': self.innodb_undo_directory,
            'innodb_undo_log_encrypt': self.innodb_undo_log_encrypt,
            'innodb_undo_log_truncate': self.innodb_undo_log_truncate,
            'innodb_max_undo_log_size': self.innodb_max_undo_log_size,
            'innodb_rollback_on_timeout': self.innodb_rollback_on_timeout,
            'innodb_rollback_segments': self.innodb_rollback_segments,
            'innodb_log_checksums': self.innodb_log_checksums,
            'innodb_checksum_algorithm': self.innodb_checksum_algorithm,
            'innodb_log_compressed_pages': self.innodb_log_compressed_pages,
            'innodb_doublewrite': self.innodb_doublewrite,
            'innodb_commit_concurrency': self.innodb_commit_concurrency,
            'innodb_read_only': self.innodb_read_only,
            'innodb_dedicated_server': self.innodb_dedicated_server,
            'innodb_buffer_pool_chunk_size': self.innodb_buffer_pool_chunk_size,
            'innodb_buffer_pool_size': self.innodb_buffer_pool_size,
            'innodb_buffer_pool_instances': self.innodb_buffer_pool_instances,
            'innodb_old_blocks_pct': self.innodb_old_blocks_pct,
            'innodb_old_blocks_time': self.innodb_old_blocks_time,
            'innodb_random_read_ahead': self.innodb_random_read_ahead,
            'innodb_read_ahead_threshold': self.innodb_read_ahead_threshold,
            'innodb_max_dirty_pages_pct_lwm': self.innodb_max_dirty_pages_pct_lwm,
            'innodb_max_dirty_pages_pct': self.innodb_max_dirty_pages_pct,
            'innodb_flush_neighbors': self.innodb_flush_neighbors,
            'innodb_lru_scan_depth': self.innodb_lru_scan_depth,
            'innodb_adaptive_flushing': self.innodb_adaptive_flushing,
            'innodb_adaptive_flushing_lwm': self.innodb_adaptive_flushing_lwm,
            'innodb_flushing_avg_loops': self.innodb_flushing_avg_loops,
            'innodb_buffer_pool_dump_pct': self.innodb_buffer_pool_dump_pct,
            'innodb_buffer_pool_dump_at_shutdown': self.innodb_buffer_pool_dump_at_shutdown,
            'innodb_buffer_pool_load_at_startup': self.innodb_buffer_pool_load_at_startup,
            'innodb_buffer_pool_filename': self.innodb_buffer_pool_filename,
            'innodb_stats_persistent': self.innodb_stats_persistent,
            'innodb_stats_on_metadata': self.innodb_stats_on_metadata,
            'innodb_stats_method': self.innodb_stats_method,
            'innodb_stats_auto_recalc': self.innodb_stats_auto_recalc,
            'innodb_stats_include_delete_marked': self.innodb_stats_include_delete_marked,
            'innodb_stats_persistent_sample_pages': self.innodb_stats_persistent_sample_pages,
            'innodb_stats_transient_sample_pages': self.innodb_stats_transient_sample_pages,
            'innodb_status_output': self.innodb_status_output,
            'innodb_status_output_locks': self.innodb_status_output_locks,
            'innodb_buffer_pool_dump_now': self.innodb_buffer_pool_dump_now,
            'innodb_buffer_pool_load_abort': self.innodb_buffer_pool_load_abort,
            'innodb_buffer_pool_load_now': self.innodb_buffer_pool_load_now,
            'innodb_thread_concurrency': self.innodb_thread_concurrency,
            'innodb_concurrency_tickets': self.innodb_concurrency_tickets,
            'innodb_thread_sleep_delay': self.innodb_thread_sleep_delay,
            'innodb_adaptive_max_sleep_delay': self.innodb_adaptive_max_sleep_delay,
            'innodb_read_io_threads': self.innodb_read_io_threads,
            'innodb_write_io_threads': self.innodb_write_io_threads,
            'innodb_use_native_aio': self.innodb_use_native_aio,
            'innodb_flush_sync': self.innodb_flush_sync,
            'innodb_io_capacity': self.innodb_io_capacity,
            'innodb_io_capacity_max': self.innodb_io_capacity_max,
            'innodb_spin_wait_delay': self.innodb_spin_wait_delay,
            'innodb_purge_threads': self.innodb_purge_threads,
            'innodb_purge_batch_size': self.innodb_purge_batch_size,
            'innodb_purge_rseg_truncate_frequency': self.innodb_purge_rseg_truncate_frequency,
            'innodb_deadlock_detect': self.innodb_deadlock_detect,
            'innodb_autoinc_lock_mode': self.innodb_autoinc_lock_mode,
            'innodb_print_all_deadlocks': self.innodb_print_all_deadlocks,
            'innodb_lock_wait_timeout': self.innodb_lock_wait_timeout,
            'innodb_table_locks': self.innodb_table_locks,
            'innodb_sync_array_size': self.innodb_sync_array_size,
            'innodb_sync_spin_loops': self.innodb_sync_spin_loops,
            'innodb_print_ddl_logs': self.innodb_print_ddl_logs,
            'innodb_replication_delay': self.innodb_replication_delay,
            'innodb_cmp_per_index_enabled': self.innodb_cmp_per_index_enabled,
            'innodb_disable_sort_file_cache': self.innodb_disable_sort_file_cache,
            'innodb_numa_interleave': self.innodb_numa_interleave,
            'innodb_strict_mode': self.innodb_strict_mode,
            'innodb_sort_buffer_size': self.innodb_sort_buffer_size,
            'innodb_fast_shutdown': self.innodb_fast_shutdown,
            'innodb_force_load_corrupted': self.innodb_force_load_corrupted,
            'innodb_force_recovery': self.innodb_force_recovery,
            'innodb_temp_tablespaces_dir': self.innodb_temp_tablespaces_dir,
            'innodb_tmpdir': self.innodb_tmpdir,
            'innodb_temp_data_file_path': self.innodb_temp_data_file_path,
            'innodb_page_cleaners': self.innodb_page_cleaners,
            'innodb_adaptive_hash_index': self.innodb_adaptive_hash_index,
            'innodb_adaptive_hash_index_parts': self.innodb_adaptive_hash_index_parts,
            'innodb_flush_log_at_timeout': self.innodb_flush_log_at_timeout,
            'innodb_flush_log_at_trx_commit': self.innodb_flush_log_at_trx_commit,
            'innodb_flush_method': self.innodb_flush_method,
            'innodb_fsync_threshold': self.innodb_fsync_threshold,
            'innodb_change_buffer_max_size': self.innodb_change_buffer_max_size,
            'innodb_change_buffering': self.innodb_change_buffering,
            'innodb_fill_factor': self.innodb_fill_factor,
            'innodb_file_per_table': self.innodb_file_per_table,
            'innodb_autoextend_increment': self.innodb_autoextend_increment,
            'innodb_open_files':self.innodb_open_files,
            'character_set_server': self.character_set_server,
            'performance_schema': self.performance_schema,
        })


    def _config_cpu(self):
        """
        配置 cpu 相关的参数
        """
        logger.info("config cpu options")
        cores = self.cores
        if cores <= 8:
            pass
        if cores <= 16:
            self.innodb_read_io_threads = 6
        elif cores <= 24:
            self.innodb_write_io_threads = 6
        elif cores <= 40:
            self.innodb_read_io_threads = 8
            self.innodb_purge_threads = 6
        elif cores <= 80:
            self.innodb_read_io_threads = 8
            self.innodb_write_io_threads = 8
            self.innodb_page_cleaners = 6
        else:
            self.innodb_read_io_threads = 8
            self.innodb_write_io_threads = 8
            self.innodb_purge_threads = 8
            self.innodb_page_cleaners = 8
        self.defaults.update({
            'innodb_read_io_threads': self.innodb_read_io_threads,
            'innodb_write_io_threads': self.innodb_write_io_threads,
            'innodb_purge_threads': self.innodb_purge_threads,
            'innodb_page_cleaners': self.innodb_page_cleaners,
        })
        logger.debug(f"change innodb_read_io_threads to {self.innodb_read_io_threads}")
        logger.debug(f"change innodb_write_io_threads to {self.innodb_write_io_threads}")
        logger.debug(f"change innodb_purge_threads to {self.innodb_purge_threads}")
        logger.debug(f"chage innodb_page_cleaners to {self.innodb_page_cleaners}")

    def _config_disk(self):
        """
        """
        logger.info("config disk options")

    def _config_mem(self):
        """
        配置 memory 相关的参数
        """
        logger.info("config memory options")
        chunk = 1
        if self.max_mem <= 512:
            chunk = 1
        elif self.max_mem <= 1024:
            chunk = 2
        elif self.max_mem <= 4096:
            # 50%
            chunk = int( (self.max_mem // 128) * 0.5 )
        elif self.max_mem <= 1024 * 8:
            # 55%
            chunk = int( (self.max_mem // 128) * 0.55 )
        elif self.max_mem <= 1024 * 16:
            # 60%
            chunk = int( (self.max_mem // 128) * 0.55 )
        elif self.max_mem <= 1024 * 32:
            # 65%
            chunk = int( (self.max_mem // 128) * 0.65 )
        elif self.max_mem <= 1024 * 64:
            # 70%
            chunk = int( (self.max_mem // 128) * 0.70 )
        elif self.max_mem <= 1024 * 128:
            # 75%
            chunk = int( (self.max_mem // 128) * 0.75 )
        elif self.max_mem <= 1024 * 256:
            chunk = int( (self.max_mem // 128) * 0.80 )
        else:
            chunk = int( (self.max_mem // 128) * 0.85 )

        # 1 innodb_buffer_pool_size
        if chunk % 4 == 0:
            # use GB
            self.innodb_buffer_pool_size = f"{int(chunk / 8)}G"
        else:
            # use MB
            self.innodb_buffer_pool_size = f"{int(chunk * 128)}M"
        logger.debug(f"change innodb_buffer_pool_size to {self.innodb_buffer_pool_size}")
        
        # 2 innodb_buffer_pool_instances
        instances = chunk // 8 if chunk >=8 else 1 # 至少每两 G 一个 instance
        if instances >= 32:
            instances = 32
        self.innodb_buffer_pool_instances = instances
        logger.debug(f"change innodb_buffer_pool_instances to {self.innodb_buffer_pool_instances}")

        # 3 performance_schema 
        self.performance_schema  = 'ON' if chunk >=8 else 'OFF'
        logger.debug(f"change performance_schema to {self.performance_schema}")

        # innodb_log_buffer_size
        # innodb_log_file_size
        if chunk >= 32:
            self.innodb_log_file_size = '256M'
            self.innodb_log_buffer_size = '256M'
        elif chunk >= 64:
            self.innodb_log_file_size = '256M'
            self.innodb_log_buffer_size = '1G'
        logger.debug(f"change innodb_log_file_size to {self.innodb_log_file_size}")
        logger.debug(f"change innodb_log_buffer_size to {self.innodb_log_buffer_size}")

        self.defaults.update({
            'innodb_buffer_pool_size': self.innodb_buffer_pool_size,
            'innodb_buffer_pool_instances': self.innodb_buffer_pool_instances,
            'performance_schema': self.performance_schema,
            'innodb_log_file_size': self.innodb_log_file_size,
            'innodb_log_buffer_size': self.innodb_log_buffer_size,
        })

    def config_all(self):
        """
        完成 cpu mem disk 相关的配置
        """
        self._config_cpu()
        self._config_mem()
        self._config_disk()

    def render(self):
        self.config_all()
        self.tmpl.globals = self.defaults
        logger.info("going to render config file")
        with common.sudo(f"render config file /etc/my-{self.port}.cnf"):
            with open(f"/etc/my-{self.port}.cnf",'w') as cnf:
                cnf.write(self.tmpl.render())


class ZabbixRender(BaseRender):
    """
    """
    pass


class MySQLSystemdRender(BaseRender):
    """
    """
    def __init__(self,tmpl_dir:str="/usr/local/dbm-agent/etc/templates/",
                      tmpl_file:str="mysqld.service.jinja",
                      pkg:str="mysql-8.0.17-linux-glibc2.12-x86_64.tar.xz",port:int=3306):
        super().__init__(tmpl_dir,tmpl_file)
        self.version = pkg.replace('.tar.gz','').replace('.tar.xz','')
        self.basedir = os.path.join('/usr/local/',self.version)
        self.port = port

        self.defaults = {
            'basedir': self.basedir,
            'port': self.port,
            'user': f'mysql{self.port}',
        }

        self.tmpl.globals = self.defaults

    def render(self):
        """
        """
        with common.sudo(f"render mysql systemd config file port = {self.port}"):
            cnf = self.tmpl.render()
            with open(f'/usr/lib/systemd/system/mysqld-{self.port}.service','w') as cnf_dst:
                cnf_dst.write(cnf)












































