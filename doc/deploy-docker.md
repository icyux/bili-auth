# Docker 部署

本项目已支持通过 Docker 直接部署，但是尚处于**测试阶段**，如您在使用过程中遇到问题或有建议请通过 Issue 提出。

## 拉取镜像

[Docker Hub: icyu/bili-auth](https://hub.docker.com/r/icyu/bili-auth)

此镜像包含 Python 运行环境、依赖包和 Selenium 环境。目前仅提供适用于 amd64 架构的镜像。请拉取最新版镜像。

您也可以通过项目提供的 Dockerfile 自行构建镜像。

## 配置

项目位于容器中的 `/app/` 目录，容器的 80 端口是 bili-auth 的 HTTP 服务端口。在构建时已初始化了一个基本的 SQLite3 数据库。

要在容器内正常运行服务，您至少需要手动配置以下项：

- 时钟与时区设置（用于正常显示时间）
- `credential.toml` 中的帐户凭据（参考[部署流程](deploy.md)的相关部分）

## 运行

直接运行容器即可。

