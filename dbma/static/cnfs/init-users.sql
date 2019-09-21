set @@sql_log_bin=0;

alter user root@'localhost' identified by 'dbma@0352';
create user root@'127.0.0.1' identified by 'dbma@0352';
grant all on *.* to root@'127.0.0.1' ;

create user dbma@'127.0.0.1' identified by 'dbma@0352';
grant all on *.* to dbma@'127.0.0.1';

create user 'clone_user'@'127.0.0.1' identified by 'dbma@0352';
grant clone_admin on *.* to 'clone_user'@'127.0.0.1';
create user 'clone_user'@'localhost' identified by 'dbma@0352';
grant clone_admin on *.* to 'clone_user'@'localhost';

create user 'clone_user'@'%' identified by 'dbma@0352';
grant backup_admin on *.* to 'clone_user'@'%';


set @@sql_log_bin=1;


