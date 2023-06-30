## 配置 redis 从库
假设主库的地址是`127.0.0.1:6382`,由于我这里是一台机器，所以从库我把端口换到了 6383 。
```bash
dbma-cli-redis --port=6383 --replica-of=127.0.0.1:6382 replica
[2023-06-30 20:08:53,442 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 250 line]  ~  starts install_redis_replica .
[2023-06-30 20:08:53,442 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 251 line]  ~  redis-port=6383, redis-master=127.0.0.1 6382, pkg=/usr/local/dbm-agent/pkgs/redis-7.0.11-linux-glibc-2.34-x86_64.tar.gz
[2023-06-30 20:08:53,442 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 29 line]  ~  starts create_redis_user .
[2023-06-30 20:08:53,554 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 35 line]  ~  ends create_redis_user .
[2023-06-30 20:08:53,554 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 68 line]  ~  starts create_redis_database_dir .
[2023-06-30 20:08:53,555 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 46 line]  ~  starts chown_database_dir_to_redis_user .
[2023-06-30 20:08:53,555 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 50 line]  ~  going to chown .
[2023-06-30 20:08:53,557 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 52 line]  ~  chown down.
[2023-06-30 20:08:53,558 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 54 line]  ~  ends chown_database_dir_to_redis_user .
[2023-06-30 20:08:53,558 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 78 line]  ~  ends create_redis_database_dir .
[2023-06-30 20:08:53,559 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 135 line]  ~  starts decompression_redis_pkg .
[2023-06-30 20:08:53,559 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 97 line]  ~  starts pkg_to_redis_basedir .
[2023-06-30 20:08:53,559 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 107 line]  ~  ends pkg_to_redis_basedir .
[2023-06-30 20:08:53,560 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 140 line]  ~  ends decompression_redis_pkg .
[2023-06-30 20:08:53,561 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/config.py 53 line]  ~  starts render_config .
[2023-06-30 20:08:53,564 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/config.py 76 line]  ~  ends render_config .
[2023-06-30 20:08:53,565 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 97 line]  ~  starts pkg_to_redis_basedir .
[2023-06-30 20:08:53,565 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 107 line]  ~  ends pkg_to_redis_basedir .
[2023-06-30 20:08:53,566 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/systemd.py 59 line]  ~  starts generate_systemd_config .
[2023-06-30 20:08:53,566 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/systemd.py 30 line]  ~  starts render_config .
[2023-06-30 20:08:53,568 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/systemd.py 51 line]  ~  ends render_config .
[2023-06-30 20:08:53,568 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/systemd.py 68 line]  ~  systemctl daemon-reload
[2023-06-30 20:08:53,718 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/systemd.py 70 line]  ~  ends generate_systemd_config .
[2023-06-30 20:08:53,741 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 256 line]  ~  ends install_redis_replica .
```
---
2、检查
```bash
ps -ef | grep redis
redis63+ 3687527       1  0 20:05 ?        00:00:00 /usr/local/redis-7.0.11/bin/redis-server *:6382
redis63+ 3688598       1  0 20:08 ?        00:00:00 /usr/local/redis-7.0.11/bin/redis-server *:6383
root     3689222 3688058  0 20:11 pts/0    00:00:00 grep --color=auto redis

# 由于它是 6382 的从库，上一节我们向 6382 写了一个值，这下应该能读出来
/usr/local/redis-7.0.11/bin/redis-cli -p 6383
127.0.0.1:6383> get pserson:001:name
"tom"
```
---