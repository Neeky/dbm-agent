set @@sql_log_bin=0;

alter user root@'localhost' identified by 'dbma@0352';
create user root@'127.0.0.1' identified by 'dbma@0352';
grant all on *.* to root@'127.0.0.1' with grant option;

create user dbma@'127.0.0.1' identified by 'dbma@0352';
grant all on *.* to dbma@'127.0.0.1' with grant option;

-- clone
create user 'cloneuser'@'127.0.0.1' identified by 'dbma@0352';
grant clone_admin,system_variables_admin on *.* to 'cloneuser'@'127.0.0.1';
create user 'cloneuser'@'localhost' identified by 'dbma@0352';
grant clone_admin,system_variables_admin on *.* to 'cloneuser'@'localhost';
create user 'cloneuser'@'%' identified by 'dbma@0352';
grant backup_admin on *.* to 'cloneuser'@'%';

-- replication
create user 'repluser'@'%' identified by 'dbma@0352';
grant replication slave,replication client on *.* to 'repluser'@'%';

-- monitor
create user monitor@'127.0.0.1' identified by 'dbma@0352';
grant replication client,process on *.* to monitor@'127.0.0.1';

set @@sql_log_bin=1;


