set @@sql_log_bin = 0;
-- 更新 root 用户
alter user root @'localhost' identified by 'dbma@0352';

create user root @'127.0.0.1' identified by 'dbma@0352';

grant all on *.* to root @'127.0.0.1' with grant option;

-- 创建 dbma 管理用户
create user dbma @'127.0.0.1' identified by 'dbma@0352';

grant all on *.* to dbma @'127.0.0.1' with grant option;

-- 创建复制用户
create user repl @'%' identified by '2-4nw9A0-459st36';

grant replication slave, replication client on *.* to repl @'%';

-- orchestrator
create user orc_server_user @'127.0.0.1' identified by 'OAi_z0v_82DBMA_E';

grant all on *.* to orc_server_user @'127.0.0.1';

create user orc_server_user @'localhost' identified by 'OAi_z0v_82DBMA_E';

grant all on *.* to orc_server_user @'localhost';

create user orc_topo_user @'127.0.0.1' identified by 'DBM_a0z_ae63Fu_S';

grant all on *.* to orc_topo_user @'127.0.0.1';

create user orc_topo_user @'localhost' identified by 'DBM_a0z_ae63Fu_S';

grant all on *.* to orc_topo_user @'localhost';

set @@sql_log_bin = 1;