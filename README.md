# bili-auth

第三方实现的哔哩哔哩 OAuth 2.0 API，无需通过官方平台申请成为开发者。应用只需通过标准的 OAuth 2.0 流程，即可快速接入哔哩哔哩帐号登录。

视频展示：[【开源】让你的应用快速接入哔哩哔哩帐号登录 | bili-auth](https://www.bilibili.com/video/BV1iS4y1S7QB)

## 对于用户

基于私信鉴权，用户仅需按照指引发送一条私信即可完成鉴权。快捷简单，用户容易接受。


## 对于开发者

后端所有功能，包括 OAuth Service / 私信收发机器人 等，均使用 `Python` 编写，使用的 Web 框架为 `Flask`。向外提供通用的 OAuth 2.0 API，开发者可以直接调用。

完全基于普通用户使用的 API ，不需要申请其他接口，无门槛。开发者只需要一个可以正常收发私信的哔哩哔哩帐号即可搭建自己的 *bili-auth* 服务。

关于环境准备、配置填写、应用管理、运行，参考 [部署流程](doc/deploy.md) 。


## Demo

在本项目的 "demo" 目录中是一个基于 `PHP` 的留言板，它需要用户通过 *bili-auth* 验证哔哩哔哩帐号后方可进行留言操作。您可自行在 PHP-FPM 环境下部署。

如果需要在线 Demo ，可以访问 [我的博客](https://blog.icyu.me) ，文章评论区已经接入 *bili-auth* ，作为其中一项登录方式。


## 其他

关于此项目的博客文章，以及 bilibili 私信 API 的更多文档：<https://blog.icyu.me/post/1626001>

关于此项目的最初设想：<https://www.bilibili.com/video/BV1TX4y1c727>
