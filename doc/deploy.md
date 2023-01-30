# 部署流程

## 初始化

在安装依赖之前，可以先使用 venv 配置虚拟环境。

通过依赖列表，安装项目所需依赖：

```sh
pip3 install -r ./requirements.txt
```

初始化数据库结构：
```sh
sqlite3 ./oauth_application.db3 < ./schema.sql
```
## 填写配置文件

配置文件为 config.toml 。除了 `uid` 和 `nickname` 需要根据实际情况填写以外，大部分配置项可以保持默认。

```toml
[bili]
	# 机器人账号的 UID。在生成跳转链接及机器人发送私信时使用。
	uid = 0
	# 机器人账号的昵称。在引导用户发送私信时使用。
	nickname = ""
	# 请求 API 使用的 User-Agent。通常不需要修改。
	user_agent = "..."

[selenium]
	# ChromeDriver 的路径。如果已经配置好环境变量则无需更改。
	path = "chromedriver"
	# 启动 ChromeDriver 时的额外选项。在运行 credential.py 时不会使用到。
	options = [
		"--headless",
		"--blink-settings=imagesEnabled=false",
	]

[proxy]
	# 代理开关。代理将会在调用需要鉴权的接口及运行 selenium 时启用。
	enable = false
	# 代理类型。目前仅支持 HTTP CONNECT 代理，因此不应更改。
	type = "http"
	# 代理地址。
	addr = "host:port"

	# 全局代理。启用后所有请求（包括请求无需鉴权的用户头像与基本信息接口），都通过代理完成。
	# 为优化 API 响应速度，默认禁用。即使禁用此项，用户归属地也不会与真实 IP 关联。
	globalProxy = false

[oauth_service]
	# HMAC 密钥，base64 编码。用于保存用户鉴权信息。默认留空，每次运行时随机生成。
	# 如果需要手动指定，可以在终端运行此命令生成：
	# head -c 64 /dev/random | base64
	hmac_key = ""

[log]
	# 日志格式。参见 <https://docs.python.org/zh-cn/3/library/logging.html#logrecord-attributes>
	format = "..."
```

HTTP 监听地址则在 `uwsgi.ini` 配置。

## 鉴权凭据生成

本项目需要您配置有效的哔哩哔哩账户凭据。您可以使用以下任意一种方式生成凭据。

### 使用脚本

项目根目录中的 `create_credential.py` 用于快速生成凭据。此脚本会通过 selenium 打开浏览器窗口并且跳转到 bilibili.com。您需要根据指示登录账号，然后凭据就会被自动保存到 credential.toml 。

由于需要您手动操作，此脚本需要在有图形界面，并且配置好 selenium 的环境运行。如果运行 Web 应用的环境没有图形界面，您也可以在其他符合要求的机器上克隆此项目，配置 selenium 路径及代理（可选）之后运行脚本，然后将生成的凭据导入 Web 应用的目录。

### 手动配置

credential.toml 中一共需要配置 `cookies` 和 `refresh_token` 两项，您也可以手动填入。首先在浏览器上登录您的账号，打开开发者工具，然后执行以下操作：

1. 随意选择一个发往 "\*.bilibili.com" 的请求，复制请求头中 `Cookie` 对应的值。cookie 中应当至少包含 "SESSDATA" 和 "bili_jct"。将这个值填入凭据文件中的 `cookies`。
2. 查看 www<nolink/>.bilibili.com 对应的本地存储中 `ac_time_value` 对应的值，可以在浏览器控制台输入 `localStorage['ac_time_value']` 来获取。将这个值填入凭据文件中的 `refresh_token` 。

## 添加 OAuth 应用

目前没有实现在 Web 应用中自助添加应用的功能，因此添加应用只能手动操作数据库完成。

存储应用信息的表名为 "app"，结构如下。其中某些字段格式没有强制约束，但是考虑到适配后续版本，建议遵循格式要求。

- **cid**：Client ID，应用的唯一编号。建议格式（正则表达式）：`/[0-9a-f]{8}/`
- **name**：应用名称。
- **url**：应用的 URL。回调地址开头必须与此字段相符，否则会拒绝授权。例如，若应用 URL 为 "https://<nolink/>example.com"，则回调地址开头也必须为这个值，此时例如 "https://<nolink/>example.com<nolink/>/callback" 就是一个合法的回调地址。
- **sec**：Client secret，应用生成 Access token 时需要用到。建议格式（正则表达式）：`/[0-9A-Za-z\-_]{20,26}/`
- **icon**：应用图标的 URL。

## 运行

上一步的依赖中应该已经安装好了 *uWSGI*，它将作为 Web 服务的容器。在项目根目录运行以下命令即可启动服务：

```sh
uwsgi --ini uwsgi.ini
```
