## 背景
如果 dbm-agent 收到请求就执行操作，这样还是太危险了；当前我们想做一个简单的处理方式，那就是在请求时加上一个简单的 dbmcenter_token 的值，如果这个值和 dbm-agent 配置文件中的值对上，那就执行操作。

---

## token 正确的情况
```bash
curl --header "Content-type:application/json;charset=utf-8;" \
--header "dbmcenter_token:528jm&PW47Q63]8F58hO0_%G" \
http://127.0.0.1:8086/apis/mysqls/3306/exists 2>/dev/null | jq
{
  "message": "",
  "error": null,
  "data": {
    "exists": true,
    "port": 3306
  }
}
```
---

## token 错误的情况
```bash
curl --header "Content-type:application/json;charset=utf-8;" \
--header "dbmcenter_token:this-is-an-error-token" \
http://127.0.0.1:8086/apis/mysqls/3306/exists 2>/dev/null | jq

{
  "message:": "enforce_token error , missing dbmcenter_token or dbmcenter_token value error, remote = '127.0.0.1' ",
  "error": "enforce_token error , missing dbmcenter_token or dbmcenter_token value error, remote = '127.0.0.1' ",
  "data": null
}
```

---

## 注意事项
默认情况下 dbm-agent 配置文件里面 dbmcenter_token 一项的值是 “” ，也就是说使用的非安全模式，一但 dbm-agent 收到请求他就会做相应的动作

---


## TODO
等 aiohttp 支持 https 之后，再加上对 https 的支持。

---