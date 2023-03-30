
```
[2023-03-30 04:46:37,203 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/views/defaultsview.py 36 line]  ~  post-request http://1.13.13.169:8086/apis/mysqls/install
[2023-03-30 04:46:37,203 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/views/defaultsview.py 66 line]  ~  port = '3306', ibps = '128M', pkg-name = 'mysql-8.0.31-linux-glibc2.12-x86_64.tar.xz', pkg = '/usr/local/dbm-agent/pkgs/mysql-8.0.31-linux-glibc2.12-x86_64.tar.xz' .
[2023-03-30 04:46:37,204 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/views/handlers.py 42 line]  ~  starts install mysql task handler .
[2023-03-30 04:46:37,204 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 66 line]  ~  check for pkg file exists or not .
[2023-03-30 04:46:37,204 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 72 line]  ~  check 3306 is installed or not.
[2023-03-30 04:46:37,204 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 238 line]  ~  starts create user and dirs port = 3306 .
[2023-03-30 04:46:37,205 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 249 line]  ~  create datadir '/database/mysql/data/3306' .
[2023-03-30 04:46:37,205 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 255 line]  ~  create binlogdir '/database/mysql/binlog/3306' .
[2023-03-30 04:46:37,210 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 263 line]  ~  ends create user and dirs .
[2023-03-30 04:46:37,211 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 328 line]  ~  starts decompression pkg .
[2023-03-30 04:46:37,211 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 338 line]  ~  ends decompression pkg .
[2023-03-30 04:46:37,211 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 372 line]  ~  starts create mysql config file. basedir = '/usr/local/mysql-8.0.31-linux-glibc2.12-x86_64', port = '3306', innodb_buffer_pool_size = '128M' .
[2023-03-30 04:46:37,211 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/config.py 429 line]  ~  starts _calcu_dep_port fun . 
[2023-03-30 04:46:37,211 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/config.py 445 line]  ~  set user to mysql3306 .
[2023-03-30 04:46:37,211 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/config.py 446 line]  ~  set datadir to /database/mysql/data/3306 .
[2023-03-30 04:46:37,212 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/config.py 447 line]  ~  set admin_port to 33062 .
[2023-03-30 04:46:37,212 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/config.py 448 line]  ~  set mysqlx_port to 33060 .
[2023-03-30 04:46:37,212 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/config.py 449 line]  ~  ends _calcu_dep_port fun . 
[2023-03-30 04:46:37,243 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/config.py 374 line]  ~  starts generate init cnf config file .
[2023-03-30 04:46:37,266 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/config.py 397 line]  ~  starts generate init cnf config file .
[2023-03-30 04:46:37,267 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/config.py 402 line]  ~  starts generate systemd config file .
[2023-03-30 04:46:37,268 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/config.py 422 line]  ~  ends generate systemd config file .
[2023-03-30 04:46:37,268 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 382 line]  ~  ends create mysql config file.
[2023-03-30 04:46:37,268 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 400 line]  ~  starts init mysql port = '3306', basedir = '/usr/local/mysql-8.0.31-linux-glibc2.12-x86_64' .
[2023-03-30 04:46:37,268 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 408 line]  ~  init-cmd = '/usr/local/mysql-8.0.31-linux-glibc2.12-x86_64/bin/mysqld --defaults-file=/tmp/mysql-8.0-init.cnf --initialize-insecure' .
[2023-03-30 04:46:49,070 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 411 line]  ~  ends init mysql.
[2023-03-30 04:46:49,071 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 123 line]  ~  start enable mysql systemd .
[2023-03-30 04:46:49,071 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 95 line]  ~  starts check mysql systemd exists 'mysqld-3306' 
[2023-03-30 04:46:49,071 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 103 line]  ~  ends check mysql systemd exists 'mysqld-3306' 
[2023-03-30 04:46:49,071 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 129 line]  ~  execute 'systemctl enable mysqld-3306' 
[2023-03-30 04:46:49,242 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 133 line]  ~  ends enable systemd '3306' 
[2023-03-30 04:46:49,243 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 183 line]  ~  starts start mysql .
[2023-03-30 04:46:49,243 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 95 line]  ~  starts check mysql systemd exists 'mysqld-3306' 
[2023-03-30 04:46:49,243 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 103 line]  ~  ends check mysql systemd exists 'mysqld-3306' 
[2023-03-30 04:46:49,243 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 189 line]  ~  execute 'systemctl start mysqld-3306' 
[2023-03-30 04:46:49,259 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 193 line]  ~  ends start mysql .
[2023-03-30 04:46:49,259 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/views/handlers.py 47 line]  ~  install mysql complete
[2023-03-30 04:46:49,259 WARNING] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/views/handlers.py 51 line]  ~  install mysql task handler's callback function is None, skip callback
[2023-03-30 04:46:49,259 INFO] - [backends_1] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/views/handlers.py 58 line]  ~  ends install mysql task handler .
```