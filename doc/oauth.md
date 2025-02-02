# 添加 OAuth 应用

打开 bili-auth > 点击右上角头像 > 点击“创建的应用” > 点击 “创建新应用”，或者直接访问 `/oauth/application/new`，在创建页面填入信息即可。

# OAuth 2.0 接入

授权页面：`/oauth/authorize?client_id=<应用编号>&redirect_uri=<回调地址>`

授权完成后，用户会被重定向到您预设的回调地址，访问码（Access Code）将以 Query param 的形式返回。
例如您要求重定向至 `https://example.com/oauth/callback`，
则用户将被重定向至 `https://example.com/oauth/callback?code=ExampleCode`。

## API

### 获取访问令牌

```http
POST /oauth/access_token
?client_id=<应用编号>
&client_secret=<应用密钥>
&code=<访问码>
```

成功响应的格式：
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
	"token": <访问令牌>,
	"user": {
		"uid": <用户 UID>,
		"name": <用户昵称>,
		"avatar": <用户头像 URL>,
		"raw_data": <B站 API 的原始响应体>
	}
}
```

### 获取用户信息


可以通过访问令牌获取：
```http
GET /api/user
Authorization: Bearer <访问令牌>
```

或者通过应用凭据获取已授权用户信息：
```http
GET /api/user
?uid=<用户 UID>
&client_id=<应用编号>
&client_secret=<应用密钥>
```

成功响应的格式：
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
	"uid": <用户 UID>,
	"name": <用户昵称>,
	"avatar": <用户头像 URL>,
	"raw_data": <B站 API 的原始响应体>"
}
```
