create table mysql_basic(
    port           int       default 3306,
    insert_time    datetime  default now,
    com_insert     bigint    default 0,
    com_delete     bigint    default 0,
    com_update     bigint    default 0,
    com_select     bigint    default 0,
    slow_query     bigint    default 0,
    bytes_received bigint    default 0,
    bytes_sent     bigint    default 0,

    primary key(insert_time,port));
create index idx_port_001 on mysql_basic(port);


create table mysql_slave(
    port                   int       default 3306,
    insert_time            datetime  default now,
    seconds_behind_master  int       default 0,
    slave_io_running       bool      default true,
    slave_sql_running      bool      default true,

    primary key(insert_time,port));
create index idx_port_002 on mysql_slave(port);


create table mysql_mgr(
    port                                int            default 3306,
    insert_time                         datetime       default now,
    member_id                           uuid           default 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    member_role                         bool char(16)  default 'PRIMARY',
    count_transactions_in_queue         bigint         default 0,
    count_transactions_rows_validating  bigint         default 0,

    primary key(insert_time,port));
create index idx_port_003 on mysql_mgr(port);

