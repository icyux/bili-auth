# bili-auth

第三方的 Bilibili OAuth 2.0 API，应用只需通过标准的 `OAuth 2.0` 流程，即可快速接入哔哩哔哩帐号登录。

视频展示：<https://www.bilibili.com/video/bv1iS4y1S7QB>

## 对于用户

基于私信鉴权，用户仅需按照指引发送一条私信即可完成鉴权。快捷简单，用户容易接受。

![鉴权与授权流程](https://blog.icyu.me/image/220607-94d8f841784b3e17.jpg)


## 对于开发者

后端所有功能，包括 OAuth Service / 私信收发机器人 等，均使用 `Python` 编写，使用的 Web 框架为 `Flask`。向外提供通用的 OAuth 2.0 API，开发者可以直接调用。

完全基于普通用户使用的 API ，不需要申请其他接口，无门槛。开发者只需要一个可以正常收发私信的哔哩哔哩帐号即可搭建自己的 *bili-auth* 服务。

主要依赖：
```text
Python >= 3.7.2
Flask >= 2.0.1

（非硬性要求，但必须有支持 f-string 的 Python 版本，以及支持处理函数直接返回字典作为 JSON 响应的 Flask 版本）
```

开发者只需填写 Cookie 等必要项即可完成配置。配置项在 "config.json" 中，格式如下：
```js
{
	"bili": {
		// user id 机器人uid，必填
		"uid": 114514,
		// cookie value
		"cookie": "登录机器人帐号后的 Cookies ，从开发者工具将 Cookie 头的内容复制过来即可，原始格式（类似 a=b; c=d; ）",
		// name will display on the verify request page
		"nickname": "机器人的昵称，用于前端展示",
		// device id (UUID), randomly generated if not specified
		"dev_id": "一般留空即可，这样将会随机生成一个设备id",
		"user_agent": "浏览器标识，一般不用自己填写，用项目默认的即可",
	},

	"oauth_service": {
		"host": "监听地址",
		"port": 8080,
		
		// base64 编码的 HMAC Key，用于后端对颁发的 token （实现类似 JWT）验证。若留空则每次启动随机生成。
		// 建议在 Shell 中运行这个命令生成：head -c 64 /dev/random | base64
		"hmac_key": "",
	},
}

```

填写完配置后，运行 "app.py" 即可。或者通过其他方式部署，Flask 实例的路径为 "service.app"。


## Demo

在本项目的 "demo" 目录中是一个基于 `PHP` 的留言板，它需要用户通过 *bili-auth* 验证哔哩哔哩帐号后方可进行留言操作。您可自行在 PHP-FPM 环境下部署。

如果需要在线 Demo ，可以访问 [我的博客](https://blog.icyu.me) ，文章评论区已经接入 *bili-auth*  ，作为其中一项登录方式。


## 其他

关于此项目的博客文章，以及 bilibili 私信 API 的更多文档：<https://blog.icyu.me/post/1626001>

关于此项目的最初设想：<https://www.bilibili.com/video/BV1TX4y1c727>
