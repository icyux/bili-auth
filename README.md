# bili-auth

实现了 Bilibili OAuth2.0 API，第四方应用可快速接入。

对于用户，仅需发送一条私信即可完成鉴权。

![私信验证演示](https://blog.icyu.me/image/220227-6f4b06b486266eb4.webp)

开发者可自行部署本项目。只需填写 Cookie 等必要项即可完成配置。

同时如果需要在线 Demo ，可以访问 [我的博客](https://blog.icyu.me) ，文章评论区已经接入 *bili-auth* 。

---

Bot 使用 `Python` 编写，使用的 Web 框架为 `Flask`。向外提供通用的 OAuth2.0 API，开发者可以直接调用。
提供了 基于 PHP 的 Demo。

关于 bilibili 私信 API：<https://blog.icyu.me/post/1626001>。
