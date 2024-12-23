# 部署流程

本项目基于 Python 3。如果您不熟悉 Python，请在部署时注意 `python` 和 `python3` 的区别（`pip` 和 `pip3` 同理）。部分 Linux 发行版预装了 Python 2，此时您需要用 `python3` 来运行 `*.py` 文件而非 `python`。

## 依赖安装

在安装依赖之前，可以先使用 venv 配置虚拟环境。

通过依赖列表，安装项目所需依赖：

```sh
pip3 install -r ./requirements.txt
```

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

配置文件为 `config.toml` 。若没有额外需求，所有配置项均可以保持默认。

```toml
[service]
	# Web 容器类型。可选"gunicorn"或"flask-default"。
	container = "gunicorn"
	# HTTP 监听地址。
	host = "localhost"
	# HTTP 监听端口
	port = 8080

[database]
	# 数据库配置。参考上一节的内容。
	type = "..."

[bili]
	# 请求 API 使用的 User-Agent。通常不需要修改，使用项目默认的即可。
	# 如果您要修改（例如遇到风控无法访问的情况），建议将其替换为主流浏览器最新版的 UA。
	user_agent = "..."

[proxy]
	# 代理开关。代理将会在调用需要鉴权的接口时启用。
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
	# 启动时运行 API 自检，用于检查能否正常访问B站 API 且不被反爬虫屏蔽，结果在日志中显示。
	biliApiTest = true

```

## 鉴权凭据生成

帐户凭据用于在访问哔哩哔哩 API 时验证身份。您可以使用以下任意一种方式配置凭据。

### ~~使用脚本~~

> 由于 Selenium 依赖暂时从项目中被移除，该方法目前暂不适用。

~~项目根目录中的 `create_credential.py` 用于快速生成凭据。此脚本会通过 Selenium 打开浏览器窗口并且跳转到 `bilibili.com`。您需要根据指示登录账号，然后凭据就会被自动保存到 `credential.toml`。~~

~~由于需要您手动操作，此脚本需要在有图形界面，并且配置好 Selenium 的环境运行。如果运行 Web 应用的环境没有图形界面，您也可以在其他符合要求的机器上克隆此项目，配置 Selenium 路径及代理（可选）之后运行脚本，然后将生成的凭据导入 Web 应用的目录。~~

### 手动配置

`credential.toml` 中一共需要配置 `cookies` 和 `refresh_token` 两项，您也可以手动填入。首先在浏览器上登录您的账号，打开开发者工具，然后执行以下操作：

1. 随意选择一个发往 `*.bilibili.com` 的请求，复制请求头中 `Cookie` 对应的值，格式形如 `a=b; c=d`。将这个值填入凭据文件中的 `cookies`。
2. 查看 `www.bilibili.com` 对应的本地存储中 `ac_time_value` 对应的值，可以在浏览器控制台输入 `localStorage['ac_time_value']` 来获取。将这个值填入凭据文件中的 `refresh_token` 。
3. 清除 `www.bilibili.com` 的 Cookies。若刷新网页后为未登录状态则操作成功。由于凭据在浏览器端自动刷新后原先凭据将失效，因此上述操作获取到的凭据不应同时在 bili-auth 和您的浏览器中使用，否则 bili-auth 中的凭据将失效。直接退出帐号同样会使当前凭据失效。您可以在执行清除站点 Cookies 的操作后，在浏览器中重新登录帐号。

## 运行

切换到 `server` 目录，运行 `run.py` 即可启动服务。
