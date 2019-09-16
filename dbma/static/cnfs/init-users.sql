set @@sql_log_bin=0;

create user dbma@'127.0.0.1' identified by 'dbmaSpr7';
grant all on *.* to dbma@'127.0.0.1';

alter user root@'localhost' identified by 'dbma@0352';

create user root@'127.0.0.1' identified by 'dbma@0352';
grant all on *.* to root@'127.0.0.1' ;

set @@sql_log_bin=1;


