# 部署流程

## 依赖安装

在安装依赖之前，可以先使用 venv 配置虚拟环境。

通过依赖列表，安装项目所需依赖：

```sh
pip3 install -r ./requirements.txt
```

## Selenium 环境配置

Selenium 用于模拟浏览器环境以完成凭据自动刷新。您需要安装 Chrome 或 Chromium，以及对应版本的 ChromeDriver，安装流程您可以在网络上自行搜索。如果您需要检查配置是否正确，您可以将 `config.toml` 中的 `seleniumTest` 的值改为 `true` 以执行自检。具体请查看下文章节的描述。

## 数据库

目前支持 SQLite3 和 MySQL (MariaDB) 两种类型的数据库。

### SQLite3（默认）
在配置文件 `config.toml` 中的 `database` 段填写如下配置：
```toml
[database]
	# 数据库类型
	type = "sqlite3"
	# 数据库文件的路径
	path = "./bili-auth.db3"
```

初始化数据库结构：
```sh
# 如果需要自定义数据库名称，则在项目根目录运行以下命令：
sqlite3 ./example.db3 < ./schema_sqlite3.sql

# 若不改变数据库默认文件名，则直接使用初始化脚本即可：
python3 ./init_sqlite3.py
```

### MySQL

在配置文件 `config.toml` 中的 `database` 段填写如下配置：

```toml
[database]
	# 数据库类型
	type = "mysql"
	# 数据库主机地址
	host = "localhost"
	# 数据库端口
	port = 3306
	# 库名称
	db = "db-name"
	# 登录用户名
	user = "user"
	# 登录密码
	pswd = "password"
```

数据库结构文件为 `schema_mysql.sql`。根据您使用的数据库客户端软件的不同，在数据库控制台执行此文件内的所有 `CREATE` 语句即可。

## 填写配置文件

配置文件为 `config.toml` 。除了 `uid` 和 `nickname` 需要根据实际情况填写以外，大部分配置项可以保持默认。

```toml
[database]
	# 数据库配置。参考上一节的内容。
	type = "..."

[bili]
	# 机器人账号的 UID。在生成跳转链接及机器人发送私信时使用。
	uid = 0
	# 机器人账号的昵称。在引导用户发送私信时使用。
	nickname = ""
	# 请求 API 使用的 User-Agent。通常不需要修改。
	user_agent = "..."

[selenium]
	# 浏览器的路径，如 /usr/bin/chromium。在 PATH 正确配置的情况下无需填写；除非您使用的是 Chromium，此时请手动设定路径。
	browserPath = ""
	# 启动 ChromeDriver 时的额外参数。在运行 credential.py 时不会使用到。
	# 如果您使用 root 用户运行本项目（例如在容器中运行），请添加 “--no-sandbox” 参数。
	options = [
		"--headless",
		"--blink-settings=imagesEnabled=false",
	]

[proxy]
	# 代理开关。代理将会在调用需要鉴权的接口及运行 Selenium 时启用。
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

# 以下为调试选项，您可以忽略。
[debug]
	# 启动时运行 Selenium 自检，用于检查 Selenium、ChromeDriver 与浏览器环境是否配置无误，结果在日志中显示。
	seleniumTest = false
```

HTTP 监听地址则在 `uwsgi.ini` 配置。

## 鉴权凭据生成

帐户凭据用于在访问哔哩哔哩 API 时验证身份。您可以使用以下任意一种方式配置凭据。

### 使用脚本

项目根目录中的 `create_credential.py` 用于快速生成凭据。此脚本会通过 selenium 打开浏览器窗口并且跳转到 bilibili.com。您需要根据指示登录账号，然后凭据就会被自动保存到 credential.toml 。

由于需要您手动操作，此脚本需要在有图形界面，并且配置好 selenium 的环境运行。如果运行 Web 应用的环境没有图形界面，您也可以在其他符合要求的机器上克隆此项目，配置 selenium 路径及代理（可选）之后运行脚本，然后将生成的凭据导入 Web 应用的目录。

### 手动配置

`credential.toml` 中一共需要配置 `cookies` 和 `refresh_token` 两项，您也可以手动填入。首先在浏览器上登录您的账号，打开开发者工具，然后执行以下操作：

1. 随意选择一个发往 `*.bilibili.com` 的请求，复制请求头中 `Cookie` 对应的值。cookie 中应当至少包含 `SESSDATA` 和 `bili_jct` 两个键，格式形如 `a=b; c=d`。将这个值填入凭据文件中的 `cookies`。
2. 查看 `www.bilibili.com` 对应的本地存储中 `ac_time_value` 对应的值，可以在浏览器控制台输入 `localStorage['ac_time_value']` 来获取。将这个值填入凭据文件中的 `refresh_token` 。
3. 清除 `www.bilibili.com` 的 Cookies。若刷新网页后为未登录状态则操作成功。由于凭据在浏览器端自动刷新后原先凭据将失效，因此上述操作获取到的凭据不应同时在 bili-auth 和您的浏览器中使用，否则 bili-auth 中的凭据将失效。直接退出帐号同样会使当前凭据失效。您可以在执行清除站点 Cookies 的操作后，在浏览器中重新登录帐号。

## 运行

上一步的依赖中应该已经安装好了 *uWSGI*，它将作为 Web 服务的容器。在项目根目录运行以下命令即可启动服务：

```sh
uwsgi --ini uwsgi.ini
```
