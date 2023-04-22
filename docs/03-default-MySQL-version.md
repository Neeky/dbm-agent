## 背景
多数情况下一个 MySQL 版本可能会在线上用上好几年，dbm-agent 默认会支持到最新的 MySQL 版本；为了不要让 dbm-agent 的已经支持的最高版本和你的默认版本有冲突，我们把它保存到了配置文件中。
```bash
cat dbm-agent.json  | jq
{
  ...
  "mysql_default_version": "8.0.33",
  ...
}
```

---

## 调整默认版本
总的来讲调整 MySQL 默认的片号要经过 3 步

1、安装新版本的 dbm-agent
```bash
pip3 install dbm-agent
```

2、更新配置文件 `/usr/local/dbm-agent/etc/dbm-agent.json`
```json {
"mysql_default_version": "xx.xx.xx"
}
```

3、重启
```bash
dbm-agent stop
dbm-agent start
```