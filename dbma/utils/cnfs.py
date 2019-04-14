"""
1、根据给定的资源信息自动化的计算出一个比较合理的 MySQL 配置文件
"""
import os
import psutil
from dbma.utils import users
from jinja2 import Environment,FileSystemLoader

__ALL__ = ['mysql_auto_config','get_host_info','MyCnf','My57Cnf','My80Cnf']

def get_package_templates_dir():
    import dbma
    d = os.path.dirname(dbma.__file__)
    template_dir = os.path.join(d,'static/cnfs')
    return template_dir

def get_host_info():
    """
    返回主机的 cpus(逻辑核心数),mem_size(内存大小G),磁盘大小，磁盘类型(ssd)
    """
    cpu_cores = psutil.cpu_count()
    mem_size,*_ = psutil.virtual_memory()
    mem_size = mem_size / (1024 * 1024 * 1024)

    for disk in psutil.disk_partitions():
        if disk.mountpoint == 'databases/':
            disk_size,*_ = psutil.disk_usage(disk.mountpoint)
            break
        elif disk.mountpoint == 'data/':
            disk_size,*_ = psutil.disk_usage(disk.mountpoint)
            break
    else:
        disk_size,*_ = psutil.disk_usage('/')
    disk_size = disk_size / (1024 * 1024 * 1024)

    return cpu_cores,mem_size,disk_size,'SSD'
    

class MyCnf(object):
    def __init__(self,cpu_cores=40,mem_size=128,disk_size=2000,disk_type='SSD',mysql_version='mysql-5.7.25-linux-glibc2.12-x86_64'):
        """
        cpu_cores: cpu 逻辑核发数量
        mem_size:  内存大小(GB)
        disk_size: 数据磁盘大小(GB)
        disk_type: 磁盘的类型(PCIE,SSD,HDD)
        """
        if cpu_cores <=0:
            raise ValueError('cpu_cors must gt 0')
        if mem_size <= 0:
            raise ValueError('mem_size must gt 0')
        if disk_size <= 0:
            raise ValueError('disk_size must gt 0')
        if disk_type not in ('PCIE','SSD','HDD'):
            raise ValueError('disk_type must in ("PCIE","SSD","HDD")')
        
        self.mem_size = mem_size
        self.cpu_cores = cpu_cores
        self.disk_size = disk_size
        self.disk_type = disk_type
        self._port = 3306
        self._version = mysql_version
        self._character_set_server = 'utf8'
        self._log_bin_trust_function_creators = 'ON'
        self._max_prepared_stmt_count = 1048576
        self._log_timestamps = 'system'
        self._read_only = 'OFF'
        self._skip_name_resolve = 'ON'
        self._auto_increment_increment = 1
        self._auto_increment_offset = 1
        self._lower_case_table_names = 'ON'
        self._secure_file_priv = ''
        self._open_files_limit = 102000
        self._max_connections = 151
        self._thread_cache_size = 32
        self._table_definition_cache = 3200
        self._table_open_cache_instances = 32

        # binlog
        self._binlog_format = 'ROW'
        self._log_bin = 'mysql-bin'
        self._binlog_rows_query_log_events = 'ON'
        self._log_slave_updates = 'ON'
        self._expire_logs_days = 7
        self._binlog_cache_size = 64*1024
        self._binlog_checksum = 'none'
        self._sync_binlog = 1
        self._slave_preserve_commit_order = 'ON'

        # other logs
        self._log_error = 'err.log'
        self._general_log = 'OFF'
        self._general_log_file = 'general.log'
        #
        self._slow_query_log = 'ON'
        self._slow_query_log_file = 'slow.log'
        self._log_queries_not_using_indexes = 'OFF'
        self._long_query_time = 2
        # gtid
        self._gtid_executed_compression_period = 1000
        self._gtid_mode = 'ON'
        self._enforce_gtid_consistency = 'ON'

        # replication
        self._skip_slave_start = 'OFF'
        self._master_info_repository = 'table'
        self._relay_log_info_repository = 'table'
        self._slave_parallel_type = 'logical_clock'
        self._slave_parallel_workers = 4
        self._rpl_semi_sync_master_enabled = 'ON'
        self._rpl_semi_sync_slave_enabled = 'ON'
        self._rpl_semi_sync_master_timeout = 1000

        # group commit
        self._binlog_group_commit_sync_delay = 100
        self._binlog_group_commit_sync_no_delay_count = 10

        # group repliction 
        self._binlog_transaction_dependency_tracking = 'WRITESET'
        self._transaction_write_set_extraction = 'XXHASH64'

        # innodb
        self._default_storage_engine = 'innodb'
        self._default_tmp_storage_engine = 'innodb'
        self._innodb_data_file_path = 'ibdata1:128M:autoextend'
        self._innodb_temp_data_file_path = 'ibtmp1:64M:autoextend'
        self._innodb_buffer_pool_filename = 'ib_buffer_pool'
        self._innodb_log_group_home_dir = './'
        self._innodb_log_files_in_group = 8
        self._innodb_log_file_size = '128M'
        self._innodb_file_per_table = 'ON'
        self._innodb_online_alter_log_max_size = '256M'
        self._innodb_open_files = 102000
        self._innodb_page_size = '16K'
        self._innodb_thread_concurrency = 0
        self._innodb_read_io_threads = 4
        self._innodb_write_io_threads = 4
        self._innodb_purge_threads = 4
        self._innodb_page_cleaners = 4
        self._innodb_print_all_deadlocks = 'ON'
        self._innodb_deadlock_detect = 'ON'
        self._innodb_lock_wait_timeout = 50
        self._innodb_spin_wait_delay = 6
        self._innodb_autoinc_lock_mode = 2
        self._innodb_flush_sync = 'OFF'
        self._innodb_io_capacity = 200
        self._innodb_io_capacity_max = 2000
        # innodb stat
        self._innodb_stats_auto_recalc = 'ON'
        self._innodb_stats_persistent = 'ON'
        self._innodb_stats_persistent_sample_pages = 20
        self._innodb_buffer_pool_size = '128M'
        self._innodb_buffer_pool_instances = 1
        self._innodb_adaptive_hash_index = 'ON'
        self._innodb_change_buffering = 'ALL'
        self._innodb_change_buffer_max_size = 25
        self._innodb_flush_neighbors = 'OFF'
        self._innodb_flush_method = 'O_DIRECT'
        self._innodb_doublewrite = 'ON'
        self._innodb_log_buffer_size = '16M'
        self._innodb_flush_log_at_timeout = 1
        self._innodb_flush_log_at_trx_commit = 1
        self._innodb_old_blocks_pct = 37
        self._innodb_old_blocks_time = 1000
        self._innodb_read_ahead_threshold = 56
        self._innodb_random_read_ahead = 'OFF'
        self._innodb_buffer_pool_dump_pct = '50'
        self._innodb_buffer_pool_dump_at_shutdown ='ON'
        self._innodb_buffer_pool_load_at_startup = 'ON'
        
        # performance schema
        self._performance_schema = 'ON'
        self._performance_schema_consumer_global_instrumentation = 'ON'
        self._performance_schema_consumer_events_stages_current = 'ON'
        self._performance_schema_consumer_events_stages_history = 'ON'
        self._performance_schema_consumer_events_stages_history_long = 'OFF'
        self._performance_schema_consumer_statements_digest = 'ON'
        self._performance_schema_consumer_events_statements_current = 'ON'
        self._performance_schema_consumer_events_statements_history = 'ON'
        self._performance_schema_consumer_events_statements_history_long ='OFF'
        self._performance_schema_consumer_events_waits_current = 'ON'
        self._performance_schema_consumer_events_waits_history = 'ON'
        self._performance_schema_consumer_events_waits_history_long = 'OFF'
 
    @property
    def port(self):
        return self._port

    @property
    def version(self):
        return self._version

    @property
    def socket(self):
        return f'/tmp/mysql{self.port}.sock'

    @property
    def user(self):
        return f'/tmp/mysql_{self.port}.sock'

    @property
    def basedir(self):
        return f'/usr/local/{self._version}/'

    @property
    def datadir(self):
        return f'/database/mysql/data/{self.port}/'
    
    @property
    def character_set_server(self):
        if 'mysql-8.0' in self.version:
            self._character_set_server = 'utf8mb4'
        return self._character_set_server

    @property
    def log_bin_trust_function_creators(self):
        return self._log_bin_trust_function_creators

    @property
    def max_prepared_stmt_count(self):
        return self._max_prepared_stmt_count

    @property
    def log_timestamps(self):
        return self._log_timestamps
    
    @property
    def read_only(self):
        return self._read_only

    @property
    def skip_name_resolve(self):
        return self._skip_name_resolve

    @property
    def auto_increment_increment(self):
        return self._auto_increment_increment
    
    @property
    def auto_increment_offset(self):
        return self._auto_increment_offset

    @property
    def lower_case_table_names(self):
        return self._lower_case_table_names
    
    @property
    def secure_file_priv(self):
        return self._secure_file_priv

    @property
    def open_files_limit(self):
        return self._open_files_limit
    
    @property
    def max_connections(self):
        if self.mem_size >= 64:
            self._max_connections = 256
        elif self.mem_size >= 128:
            self._max_connections = self.mem_size * 4
        
        if self._max_connections >= 1024:
            self._max_connections = 1024
        
        return self._max_connections

    @property
    def thread_cache_size(self):
        if self.mem_size <= 4:
            self._thread_cache_size = self.mem_size * 4
        elif self.mem_size <= 16:
            self._thread_cache_size = 16 if self.mem_size * 3 <= 16 else self.mem_size * 3
        elif self.mem_size <= 64:
            self._thread_cache_size = 48 if self.mem_size * 2 <= 48 else self.mem_size * 2
        
        if self._thread_cache_size >= 256:
            self._thread_cache_size = 256

    @property
    def table_definition_cache(self):
        return self._table_definition_cache
    
    @property
    def table_open_cache_instances(self):
        return self._table_open_cache_instances

    @property
    def binlog_format(self):
        return self._binlog_format

    @property
    def log_bin(self):
        return self._log_bin

    @property
    def binlog_rows_query_log_events(self):
        return self._binlog_rows_query_log_events

    @property
    def log_slave_updates(self):
        return self._log_slave_updates
    
    @property
    def expire_logs_days(self):
        return self._expire_logs_days

    @property
    def binlog_cache_size(self):
        return self._binlog_cache_size

    @property
    def binlog_checksum(self):
        return self._binlog_checksum
    
    @property
    def sync_binlog(self):
        return self._sync_binlog

    @property
    def slave_preserve_commit_order(self):
        return self._slave_preserve_commit_order
    
    @property
    def log_error(self):
        return self._log_error

    @property
    def general_log(self):
        return self._general_log

    @property
    def general_log_file(self):
        return self._general_log_file

    @property
    def slow_query_log(self):
        return self._slow_query_log

    @property
    def slow_query_log_file(self):
        return self._slow_query_log_file

    @property
    def log_queries_not_using_indexes(self):
        return self._log_queries_not_using_indexes
    
    @property
    def long_query_time(self):
        return self._long_query_time

    @property
    def gtid_executed_compression_period(self):
        return self._gtid_executed_compression_period

    @property
    def gtid_mode(self):
        return self._gtid_mode

    @property
    def enforce_gtid_consistency(self):
        return self._enforce_gtid_consistency

    @property
    def skip_slave_start(self):
        return self._skip_slave_start
    
    @property
    def master_info_repository(self):
        return self._master_info_repository

    @property
    def relay_log_info_repository(self):
        return self._relay_log_info_repository

    @property
    def slave_parallel_type(self):
        return self._slave_parallel_type   

    @property
    def slave_parallel_workers(self):
        if self.cpu_cores >= 8 :
            self.slave_parallel_workers = 8
        elif self.cpu_cores >= 24:
            self.slave_parallel_workers = 12
        elif self.cpu_cores >= 40:
            self.slave_parallel_workers = 16
        return self._slave_parallel_workers
    
    @property
    def rpl_semi_sync_master_enabled(self):
        return self._rpl_semi_sync_master_enabled
    
    @property
    def rpl_semi_sync_slave_enabled(self):
        return self._rpl_semi_sync_slave_enabled

    @property
    def rpl_semi_sync_master_timeout(self):
        return self._rpl_semi_sync_master_timeout

    @property
    def binlog_group_commit_sync_delay(self):
        return self._binlog_group_commit_sync_delay
    
    @property
    def binlog_group_commit_sync_no_delay_count(self):
        return self._binlog_group_commit_sync_no_delay_count
    
    @property
    def binlog_transaction_dependency_tracking(self):
        return self._binlog_transaction_dependency_tracking

    @property
    def default_storage_engine(self):
        return self._default_storage_engine 

    @property
    def default_tmp_storage_engine(self):
        return self._default_tmp_storage_engine

    @property
    def innodb_data_file_path(self):
        return self._innodb_data_file_path

    @property
    def innodb_temp_data_file_path(self):
        return self._innodb_temp_data_file_path

    @property
    def innodb_buffer_pool_filename(self):
        return self._innodb_buffer_pool_filename

    @property
    def innodb_log_group_home_dir(self):
        return self._innodb_log_group_home_dir

    @property
    def innodb_log_files_in_group(self):
        if self.disk_size >= 500:
            self._innodb_log_files_in_group = 12
        elif self.disk_size >= 1000:
            self._innodb_log_files_in_group = 16
        return self._innodb_log_files_in_group

    @property
    def innodb_log_file_size(self):
        return self._innodb_log_file_size

    @property
    def innodb_file_per_table(self):
        return self._innodb_file_per_table

    @property
    def innodb_online_alter_log_max_size(self):
        return self._innodb_online_alter_log_max_size

    @property
    def innodb_open_files(self):
        return self._innodb_open_files

    @property
    def innodb_page_size(self):
        return self._innodb_page_size

    @property
    def innodb_thread_concurrency(self):
        return self._innodb_thread_concurrency
    
    @property
    def innodb_read_io_threads(self):
        if self.cpu_cores >= 20:
            self._innodb_read_io_threads = 6
        elif self.cpu_cores >= 40:
            self._innodb_read_io_threads = 8
        return self._innodb_read_io_threads
    
    @property
    def innodb_write_io_threads(self):
        if self.cpu_cores >= 20:
            self._innodb_write_io_threads =6
        elif self.cpu_cores >= 40:
            self._innodb_write_io_threads = 8
        return self._innodb_write_io_threads
    
    @property
    def innodb_purge_threads(self):
        if self.cpu_cores >= 40:
            self._innodb_purge_threads = 6
        return self._innodb_purge_threads

    @property
    def innodb_page_cleaners(self):
        if self.cpu_cores >= 32:
            self._innodb_page_cleaners = 6
        elif self.cpu_cores >= 40:
            self._innodb_page_cleaners = 8
        else:
            self._innodb_page_cleaners = 12
        return self._innodb_page_cleaners

    @property
    def innodb_print_all_deadlocks(self):
        return self._innodb_print_all_deadlocks    

    @property
    def innodb_deadlock_detect(self):
        return self._innodb_deadlock_detect
    
    @property
    def innodb_lock_wait_timeout(self):
        return self._innodb_lock_wait_timeout

    @property
    def innodb_spin_wait_delay(self):
        return self._innodb_spin_wait_delay
    
    @property
    def innodb_autoinc_lock_mode(self):
        return self._innodb_autoinc_lock_mode

    @property
    def innodb_flush_sync(self):
        return self._innodb_flush_sync
    
    @property
    def innodb_io_capacity(self):
        if self.disk_type == 'PCIE':
            self._innodb_io_capacity = 8000
        elif self.disk_type == 'SSD':
            self._innodb_io_capacity = 4000
        return self._innodb_io_capacity
    
    @property
    def innodb_io_capacity_max(self):
        if self.disk_type == "PCIE":
            self._innodb_io_capacity_max = 32000
        elif self.disk_type == 'SSD':
            self._innodb_io_capacity_max = 16000
        return self._innodb_io_capacity_max

    @property
    def innodb_stats_auto_recalc(self):
        return self._innodb_stats_auto_recalc

    @property
    def innodb_stats_persistent(self):
        return self._innodb_stats_persistent

    @property
    def innodb_stats_persistent_sample_pages(self):
        if self.disk_type in ('SSD','PCIE') and self.cpu_cores >= 16:
            self._innodb_stats_persistent_sample_pages = 32
        elif self.disk_type in ('SSD','PCIE') and self.cpu_cores >= 40:
            self._innodb_stats_persistent_sample_pages = 40
        return self._innodb_stats_persistent_sample_pages

    @property
    def innodb_buffer_pool_size(self):
        if self.mem_size <= 0.25:
            # 1 / 4 G ~ 256M 如果主机的内存只有 256M 那么怎么也不调整(使用的默认的128M内存)
            pass
        elif self.mem_size <= 0.5:
            # 1 /2 ~ 512M   如果主机的内存只有 512M 那么怎么调整到 256M
            self._innodb_buffer_pool_size = '256M'
        elif self.mem_size <= 0.75:
            self._innodb_buffer_pool_size = '256M'
        elif self.mem_size <= 1:
            self._innodb_buffer_pool_size = '512M'
        elif self.mem_size <= 8:
            # mem < 8G --> 50%
            gunit = round( self.mem_size * 0.5 )
            self._innodb_buffer_pool_size = f'{gunit}G'
        elif self.mem_size <= 16:
            # 8G < mem < 16G  --> 55%
            gunit = round(self.mem_size * 0.55)
            self._innodb_buffer_pool_size = f'{gunit}G'
        elif self.mem_size <= 32:
            # 16G < mem < 32G  --> 60%
            gunit = round(self.mem_size * 0.6)
            self._innodb_buffer_pool_size = f'{gunit}G'
        elif self.mem_size <= 64:
            gunit = round(self.mem_size * 0.7)
            self._innodb_buffer_pool_size = f'{gunit}G'
        elif self.mem_size <= 128:
            gunit = round(self.mem_size * 0.75)
            self._innodb_buffer_pool_size = f'{gunit}G'
        elif self.mem_size <= 256:
            gunit = round(self.mem_size * 0.8)
            self._innodb_buffer_pool_size = f'{gunit}G'
        else:
            gunit = round(self.mem_size * 0.9)
            self._innodb_buffer_pool_size = f'{gunit}G'
        return self._innodb_buffer_pool_size
    
    @property
    def innodb_buffer_pool_instances(self):
        if 'M' in self.innodb_buffer_pool_size:
            return self._innodb_buffer_pool_instances # 返回默认的 1
        elif 'G' in self.innodb_buffer_pool_size:
            size,_ = self.innodb_buffer_pool_size.split('G')
            unit = int(int(size) / 2)
            if unit >= 16:
                unit = 16
            self._innodb_buffer_pool_instances = unit
            return self._innodb_buffer_pool_instances
        return self._innodb_buffer_pool_instances

    @property
    def innodb_adaptive_hash_index(self):
        return self._innodb_adaptive_hash_index

    @property
    def innodb_change_buffering(self):
        return self._innodb_change_buffering

    @property
    def innodb_change_buffer_max_size(self):
        return self._innodb_change_buffer_max_size

    @property
    def innodb_flush_neighbors(self):
        if self.disk_type == 'HDD':
            self._innodb_flush_neighbors = 'ON'
        return self._innodb_flush_neighbors
    
    @property
    def innodb_flush_method(self):
        return self._innodb_flush_method

    @property
    def innodb_doublewrite(self):
        return self._innodb_doublewrite

    @property
    def innodb_log_buffer_size(self):
        if self.mem_size <= 0.25:
            self._innodb_log_buffer_size = '16M'
        elif self.mem_size <= 0.5:
            self._innodb_log_buffer_size = '24M'
        elif self.mem_size <= 1:
            self._innodb_log_buffer_size = '32M'
        elif self.mem_size <= 2:
            self._innodb_log_buffer_size = '48M'
        elif self.mem_size <= 4:
            self._innodb_log_buffer_size = '64M'
        elif self.mem_size <= 8:
            self._innodb_log_buffer_size = '96M'
        elif self.mem_size <= 16:
            self._innodb_log_buffer_size = '128M'
        elif self.mem_size <= 32:
            self._innodb_log_buffer_size = '256M'
        else:
            self._innodb_log_buffer_size = '1G'
        return self._innodb_log_buffer_size
    
    @property
    def innodb_flush_log_at_timeout(self):
        return self._innodb_flush_log_at_timeout

    @property
    def innodb_flush_log_at_trx_commit(self):
        return self._innodb_flush_log_at_trx_commit
    
    @property
    def innodb_old_blocks_pct(self):
        return self._innodb_old_blocks_pct
    
    @property
    def innodb_old_blocks_time(self):
        return self._innodb_old_blocks_time

    @property
    def innodb_read_ahead_threshold(self):
        return self._innodb_read_ahead_threshold

    @property
    def innodb_random_read_ahead(self):
        if self.disk_type == 'HDD':
            self._innodb_random_read_ahead = 'ON'
        return self._innodb_random_read_ahead

    @property
    def innodb_buffer_pool_dump_pct(self):
        return self._innodb_buffer_pool_dump_pct

    @property
    def innodb_buffer_pool_dump_at_shutdown(self):
        return self._innodb_buffer_pool_dump_at_shutdown

    @property
    def innodb_buffer_pool_load_at_startup(self):
        return self._innodb_buffer_pool_load_at_startup

    @property
    def performance_schema(self):
        return self._performance_schema

    @property
    def performance_schema_consumer_global_instrumentation(self):
        return self._performance_schema_consumer_global_instrumentation
    
    @property
    def performance_schema_consumer_events_stages_current(self):
        return self._performance_schema_consumer_events_stages_current

    @property
    def performance_schema_consumer_events_stages_history(self):
        return self._performance_schema_consumer_events_stages_history
    
    @property
    def performance_schema_consumer_statements_digest(self):
        return self._performance_schema_consumer_statements_digest

    @property
    def performance_schema_consumer_events_statements_current(self):
        return self._performance_schema_consumer_events_statements_current
    
    @property
    def performance_schema_consumer_events_statements_history(self):
        return self._performance_schema_consumer_events_statements_history

    @property
    def performance_schema_consumer_events_statements_history_long(self):
        return self._performance_schema_consumer_events_statements_history_long

    @property
    def performance_schema_consumer_events_waits_current(self):
        return self._performance_schema_consumer_events_waits_current

    @property
    def performance_schema_consumer_events_waits_history(self):
        return self._performance_schema_consumer_events_waits_history

    @property
    def performance_schema_consumer_events_waits_history_long(self):
        return self._performance_schema_consumer_events_waits_history_long
    
    def write_cnf_file(self,cnf_template):
        raise NotImplementedError('MyCnf.write_cnf_file is not emplemented')
    
    def write_systemd_file(self,systemd_template):
        raise NotImplementedError('MyCnf.write_systemd_file is not emplemented')

    def change_to_mgr_mode(self):
        raise NotImplementedError('MyCnf.change_to_mgr_mode is not emplemented')


class My57Cnf(MyCnf):
    def __init__(self,cpu_cores=40,mem_size=128,disk_size=2000,disk_type='SSD',mysql_version='mysql-5.7.25-linux-glibc2.12-x86_64'):
        if 'mysql-5.7' not in mysql_version:
            raise ValueError('mysql_version must be like "mysql-5.7.xx.-linux-glibcx.xx.-x86_64" ')
        super().__init__(cpu_cores,mem_size,disk_size,disk_type,mysql_version)

    def write_cnf_file(self,cnf_template_dir='/usr/local/dbm-agent/etc/cnfs/',tpath=None):
        """
        渲染my.cnf 文件到 tpath ，在 tpath 为 None 的时候直接渲染到 /etc/my{self.port}.cnf
        """
        loader = FileSystemLoader([cnf_template_dir,get_package_templates_dir()])
        env = Environment(loader=loader)
        my57cnf = env.get_template('5_7.cnf.jinja')
        if tpath == None:
            tpath = f'/etc/my{self.port}.cnf'
        with users.sudo(f'su root for create mysql config file {tpath}'):
            with open(f'{tpath}','w') as cnf_file_obj:
                cnf_file_obj.write(my57cnf.render(cnf=self))

    def write_mysqld_file(self,cnf_template_dir='/usr/local/dbm-agent/etc/cnfs/',tpath=None):
        """
        渲染 mysqld.service 文件到 tpath ，在 tpath 为 None 的时候直接渲染到 /etc/mysqld{self.port}.cnf
        """
        loader = FileSystemLoader([cnf_template_dir,get_package_templates_dir()])
        env = Environment(loader=loader)
        mysqld_service = env.get_template('mysqld.service.jinja')
        if tpath == None:
            tpath = f'/usr/lib/systemd/system/mysqld{self.port}.service'
        with users.sudo('su root for create file ' + tpath):
            with open(tpath,'w') as mysqld_file_obj:
                mysqld_file_obj.write(mysqld_service.render(cnf=self))
    

class My80Cnf(MyCnf):
    def __init__(self,cpu_cores=40,mem_size=128,disk_size=2000,disk_type='SSD',mysql_version='mysql-8.0.14-linux-glibc2.12-x86_64'):
        if 'mysql-8.0' not in mysql_version:
            raise ValueError('mysql_version must be like "mysql-8.0.xx.-linux-glibcx.xx.-x86_64" ')
        super().__init__(cpu_cores,mem_size,disk_size,disk_type,mysql_version)
        self._sql_require_primary_key = 'ON'
        self._cte_max_recursion_depth = 1000
        self._auto_generate_certs = 'ON'
    
    @property
    def sql_require_primary_key(self):
        return self._sql_require_primary_key
    
    @property
    def cte_max_recursion_depth(self):
        return self._cte_max_recursion_depth

    @property
    def auto_generate_certs(self):
        return self._auto_generate_certs

    

    def write_cnf_file(self,cnf_template_dir='/usr/local/dbm-agent/etc/cnfs/',tpath=None):
        """
        渲染my.cnf 文件到 tpath ，在 tpath 为 None 的时候直接渲染到 /etc/my{self.port}.cnf
        """
        loader = FileSystemLoader([cnf_template_dir,get_package_templates_dir()])
        env = Environment(loader=loader)
        my57cnf = env.get_template('8_0.cnf.jinja')
        if tpath == None:
            tpath = f'/etc/my{self.port}.cnf'
        with users.sudo(f'su root for create mysql config file {tpath}'):
            with open(f'{tpath}','w') as cnf_file_obj:
                cnf_file_obj.write(my57cnf.render(cnf=self))

    def write_mysqld_file(self,cnf_template_dir='/usr/local/dbm-agent/etc/cnfs/',tpath=None):
        """
        渲染 mysqld.service 文件到 tpath ，在 tpath 为 None 的时候直接渲染到 /etc/mysqld{self.port}.cnf
        """
        loader = FileSystemLoader([cnf_template_dir,get_package_templates_dir()])
        env = Environment(loader=loader)
        mysqld_service = env.get_template('mysqld.service.jinja')
        if tpath == None:
            tpath = f'/usr/lib/systemd/system/mysqld{self.port}.service'
        with users.sudo('su root for create file ' + tpath):
            with open(tpath,'w') as mysqld_file_obj:
                mysqld_file_obj.write(mysqld_service.render(cnf=self))
    

def mysql_auto_config(cpu_cores=40,mem_size=128,disk_size=2000,disk_type='SSD',mysql_version='mysql-5.7.25-linux-glibc2.12-x86_64',ismgr=False):
    """
    MyCnf 的工厂方法
    """
    # 目前还不支持 mgr 的配置
    if ismgr == True:
        raise ValueError('current mgr is not suported')
    # 根据不同的版本生成不同的对象
    if 'mysql-5.7' in mysql_version:
        cnf = My57Cnf(cpu_cores,mem_size,disk_size,disk_type,mysql_version)
    elif 'mysql-8.0' in mysql_version:
        cnf = My80Cnf(cpu_cores,mem_size,disk_size,disk_type,mysql_version)
    else:
        raise ValueError('dbm only suport mysql-8.0 & mysql-5.7')
    # 增加上 mgr 相关的配置
    if ismgr == True:
        cnf.change_to_mgr_mode()
    
    return cnf
 