
- [通过wait分析性能问题](#通过wait分析性能问题)
- [找出谁持有metadatalock](#找出谁持有metadatalock)
- [找出谁持有行级锁](#找出谁持有行级锁)

---


## 通过wait分析性能问题
   **1、启用 wait 相关的监控项**
   ```sql
   use performance_schema;
   
   -- 生产
   update setup_instruments set enabled='YES',timed='YES' where name like 'wait%';

   -- 消费
   update setup_consumers set enabled='YES' where name like 'events_waits%';
   ``` 

   **2、查看当前是什么在等待资源**
   ```sql
   use performance_schema;
   select 
        event_name,
        operation,
        sys.format_time(sum(timer_wait)) as timer_wait,
        sys.format_bytes(sum(number_of_bytes)) as bytes
        from events_waits_current 
        where event_name != 'idle' 
        group by event_name,operation
        order by timer_wait desc
        limit 11;
        
   ```

   **3、空闲实例的表现**
   ```sql
   -- 空闲实例通常来说看到的是 wait/synch 并且 timer_wait 比较小
   +--------------------------------------------------+-----------+------------+-------+
   | event_name                                       | operation | timer_wait | bytes |
   +--------------------------------------------------+-----------+------------+-------+
   | wait/synch/mutex/sql/THD::LOCK_query_plan        | lock      | 96.60 ns   | NULL  |
   | wait/synch/mutex/innodb/log_write_notifier_mutex | lock      | 782.46 ns  | NULL  |
   | wait/synch/mutex/innodb/log_closer_mutex         | lock      | 752.10 ns  | NULL  |
   | wait/synch/mutex/innodb/log_writer_mutex         | lock      | 658.95 ns  | NULL  |
   | wait/synch/mutex/innodb/dict_sys_mutex           | lock      | 608.58 ns  | NULL  |
   | wait/synch/mutex/innodb/log_flush_notifier_mutex | lock      | 605.82 ns  | NULL  |
   | wait/synch/mutex/innodb/log_limits_mutex         | lock      | 58.65 ns   | NULL  |
   | wait/synch/mutex/innodb/recalc_pool_mutex        | lock      | 550.62 ns  | NULL  |
   | wait/synch/mutex/innodb/sync_array_mutex         | lock      | 54.51 ns   | NULL  |
   | wait/synch/mutex/sql/LOCK_thread_cache           | lock      | 45.20 ns   | NULL  |
   | wait/synch/mutex/innodb/clone_sys_mutex          | lock      | 44.16 ns   | NULL  |
   +--------------------------------------------------+-----------+------------+-------+
   11 rows in set (0.00 sec)
   ```

   ---

## 找出谁持有metadatalock
   **1、锁表**
   ```sql
   -- session A
   select * from tempdb.t for share;
   ```
   **2、执行 DDL**
   ```sql
   -- session B
   alter table tempdb.t engine=innodb;
   ``` 
   **2、查看表锁**
   ```sql
   -- session C
   -- 常规的 show processlist 看不出问题的
   show processlist;
   +-----+---------+-----------------+--------------------+---------+------+---------------------------------+-----------------------------+
   | Id  | User    | Host            | db                 | Command | Time | State                           | Info                        |
   +-----+---------+-----------------+--------------------+---------+------+---------------------------------+-----------------------------+
   |   7 | monitor | 127.0.0.1:33282 | NULL               | Sleep   |    1 |                                 | NULL                        |
   |  11 | root    | 127.0.0.1:33290 | performance_schema | Sleep   |   13 |                                 | NULL                        |
   | 225 | root    | 127.0.0.1:33718 | performance_schema | Query   |    0 | starting                        | show processlist            |
   | 328 | root    | 127.0.0.1:33924 | tempdb             | Query   |    2 | Waiting for table metadata lock | alter table t engine=innodb |
   +-----+---------+-----------------+--------------------+---------+------+---------------------------------+-----------------------------+
   
   -- 借助 performance_schema 来看是哪个
   select 
    processlist_id,
    concat(object_schema,'.',object_name) as objects,
    lock_status,
    lock_type,
    owner_thread_id
    from metadata_locks as a  join threads as b
        on a.owner_thread_id = b.thread_id
    where 
        object_name is not NULL and object_schema is not NULL and 
        owner_thread_id != sys.ps_thread_id(connection_id()) and 
        object_schema != 'performance_schema'
    order by processlist_id,objects;

   +----------------+---------------------+-------------+-------------------+-----------------+
   | processlist_id | objects             | lock_status | lock_type         | owner_thread_id |
   +----------------+---------------------+-------------+-------------------+-----------------+
   |             11 | tempdb.t            | GRANTED     | SHARED_WRITE      |              51 |
   |            328 | tempdb.#sql-56a_148 | GRANTED     | EXCLUSIVE         |             368 |
   |            328 | tempdb.t            | GRANTED     | SHARED_UPGRADABLE |             368 |
   |            328 | tempdb.t            | PENDING     | EXCLUSIVE         |             368 | -- lock_status == PENDING 说明是它在等
   +----------------+---------------------+-------------+-------------------+-----------------+
   4 rows in set (0.00 sec)

   -- 看哪个连接的所有锁状态都是 granted ，说明锁就是被谁持有了
   ```
   >如果只要解决阻塞 `kill 51;` 就可以了。但是通常想知道是为什么
   **3、查看线程对应的SQL语句** 
   ```sql
   select thread_id,sql_text from events_statements_current where thread_id = 51;
   +-----------+-----------------------------------+
   | thread_id | sql_text                          |
   +-----------+-----------------------------------+
   |        51 | select * from tempdb.t for update |
   +-----------+-----------------------------------+
   1 row in set (0.01 sec)
   ```

   ---

## 找出谁持有行级锁
   **1、排他锁定一行**
   ```sql
   -- session A
   mysql> select * from t;                                                                           
   +----+------+
   | id | x    |
   +----+------+
   |  1 |  100 |
   +----+------+
   1 row in set (0.00 sec)
   
   mysql> begin;                                                                                     
   Query OK, 0 rows affected (0.00 sec)
   
   mysql> select * from t where id = 1 for update;
   +----+------+
   | id | x    |
   +----+------+
   |  1 |  100 |
   +----+------+
   1 row in set (0.00 sec)
   ``` 
   **2、查看行锁**
   ```sql
   -- sesion B
   select thread_id,concat(object_schema,'.',object_name) as objects,lock_type,lock_mode,lock_status,lock_data from performance_schema.data_locks;
   +-----------+----------+-----------+---------------+-------------+-----------+
   | thread_id | objects  | lock_type | lock_mode     | lock_status | lock_data |
   +-----------+----------+-----------+---------------+-------------+-----------+
   |        51 | tempdb.t | TABLE     | IX            | GRANTED     | NULL      |
   |        51 | tempdb.t | RECORD    | X,REC_NOT_GAP | GRANTED     | 1         |
   +-----------+----------+-----------+---------------+-------------+-----------+
   2 rows in set (0.00 sec)

   -- 因为还没有第二个进程要给 id = 1 的行上锁，所以 data_lock_waits 里看不到数据
   select * from data_lock_waits;                                                             
   Empty set (0.01 sec)

   ``` 

   **3、用另一个会话上共享锁**
   ```sql
   -- session C
   -- 给 id = 1 的行上共享锁
   select * from tempdb.t where id = 1 for share;
   ```
   **4、查看 data_lock_waits 的内容**
   ```sql
   select 
    blocking_thread_id,
    requesting_thread_id,
    b.processlist_id as you_should_kill_ps_id 
    from data_lock_waits as a join threads as b
        on a.blocking_thread_id = b.thread_id;
   +--------------------+----------------------+-----------------------+
   | blocking_thread_id | requesting_thread_id | you_should_kill_ps_id |
   +--------------------+----------------------+-----------------------+
   |                 51 |                  368 |                    11 |
   +--------------------+----------------------+-----------------------+
   1 row in set (0.00 sec)

   -- show processlist 看到的内容如下
   show processlist;
   +-----+---------+-----------------+--------------------+---------+------+------------+-----------------------------------------------+
   | Id  | User    | Host            | db                 | Command | Time | State      | Info                                          |
   +-----+---------+-----------------+--------------------+---------+------+------------+-----------------------------------------------+
   |   7 | monitor | 127.0.0.1:33282 | NULL               | Sleep   |    2 |            | NULL                                          |
   |  11 | root    | 127.0.0.1:33290 | tempdb             | Sleep   | 1135 |            | NULL                                          |
   | 225 | root    | 127.0.0.1:33718 | performance_schema | Query   |    0 | starting   | show processlist                              |
   | 328 | root    | 127.0.0.1:33924 | tempdb             | Query   |    3 | statistics | select * from tempdb.t where id = 1 for share |
   +-----+---------+-----------------+--------------------+---------+------+------------+-----------------------------------------------+
   4 rows in set (0.00 sec)
   ``` 

   ---