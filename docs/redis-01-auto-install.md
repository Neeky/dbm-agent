## redis 自动安装
1、安装
```
dbma-cli-redis --port=6382 master

[2023-06-30 20:05:24,405 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 228 line]  ~  starts install_resdis_master .
[2023-06-30 20:05:24,406 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 29 line]  ~  starts create_redis_user .
[2023-06-30 20:05:24,590 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 35 line]  ~  ends create_redis_user .
[2023-06-30 20:05:24,590 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 68 line]  ~  starts create_redis_database_dir .
[2023-06-30 20:05:24,591 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 46 line]  ~  starts chown_database_dir_to_redis_user .
[2023-06-30 20:05:24,591 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 50 line]  ~  going to chown .
[2023-06-30 20:05:24,593 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 52 line]  ~  chown down.
[2023-06-30 20:05:24,594 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 54 line]  ~  ends chown_database_dir_to_redis_user .
[2023-06-30 20:05:24,594 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 78 line]  ~  ends create_redis_database_dir .
[2023-06-30 20:05:24,594 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 135 line]  ~  starts decompression_redis_pkg .
[2023-06-30 20:05:24,595 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 97 line]  ~  starts pkg_to_redis_basedir .
[2023-06-30 20:05:24,595 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 107 line]  ~  ends pkg_to_redis_basedir .
[2023-06-30 20:05:24,596 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 140 line]  ~  ends decompression_redis_pkg .
[2023-06-30 20:05:24,597 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/config.py 53 line]  ~  starts render_config .
[2023-06-30 20:05:24,601 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/config.py 76 line]  ~  ends render_config .
[2023-06-30 20:05:24,601 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 97 line]  ~  starts pkg_to_redis_basedir .
[2023-06-30 20:05:24,602 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 107 line]  ~  ends pkg_to_redis_basedir .
[2023-06-30 20:05:24,602 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/systemd.py 59 line]  ~  starts generate_systemd_config .
[2023-06-30 20:05:24,603 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/systemd.py 30 line]  ~  starts render_config .
[2023-06-30 20:05:24,604 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/systemd.py 51 line]  ~  ends render_config .
[2023-06-30 20:05:24,605 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/systemd.py 68 line]  ~  systemctl daemon-reload
[2023-06-30 20:05:24,753 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/systemd.py 70 line]  ~  ends generate_systemd_config .
[2023-06-30 20:05:24,995 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/redis/install.py 233 line]  ~  ends install_resdis_master .
```
---

2、检查
```bash
ps -ef | grep redis
redis63+ 3687527       1  0 20:05 ?        00:00:00 /usr/local/redis-7.0.11/bin/redis-server *:6382
root     3688087 3688058  0 20:07 pts/0    00:00:00 grep --color=auto redis


/usr/local/redis-7.0.11/bin/redis-cli -p 6382
127.0.0.1:6381> set pserson:001:name "tom"
OK
127.0.0.1:6381> get pserson:001:name
"tom"
127.0.0.1:6381>
```

---