# WeCom-Push
​	封装了企业微信推送API函数，便于使用。

#### 运行环境

- Python3

#### 特性

- 灵活获取access_token，而不是每次发送消息时都获取一次。
- 用户相关配置信息单独写在配置文件中，与函数分离。
- 支持普通文本消息和文本卡片消息。

#### 示例

- 不使用配置文件

```python
import msg

ENTERPRISE_ID = "" 
APP_SECRET = ""
APP_ID = xxxx

MsgMgr = msg.WeComPush(ENTERPRISE_ID, APP_ID, APP_SECRET)
MsgMgr.pushMsg("test")
MsgMgr.pushCardMsg("测试消息", "test")
```

- 使用配置文件

```python
import msg

MsgMgr = msg.WeComPush()
MsgMgr.pushMsg("test")
MsgMgr.pushCardMsg("测试消息", "test")
```

#### 参考

- [企业微信API文档](https://work.weixin.qq.com/api/doc/90000/90135/90250)