# 自建梯子与 IP 防泄露指南

[![Validate](https://github.com/makerkitt/vps-privacy-guide/actions/workflows/validate.yml/badge.svg)](https://github.com/makerkitt/vps-privacy-guide/actions/workflows/validate.yml)

**从一台 VPS 开始，搭建自己的代理，并检查真实 IP 有没有绕过代理暴露。**

这份中文教程带你完成购买服务器、部署节点、连接设备，以及 DNS、IPv6、WebRTC 和断线情况下的泄露检查。服务端使用 **S-UI + sing-box**，提供 **AnyTLS、Hysteria2、VLESS + Reality** 三种入口。

## 先准备一台 VPS

没有服务器，可以从这里查看搬瓦工的套餐和机房：

**[查看搬瓦工 VPS 套餐 →](https://bandwagonhost.com/aff.php?aff=82641)**

> 这是推广链接，通过它购买，作者可能获得佣金。价格、库存、线路和退款条件以官网为准。已有合适的 VPS 可以直接使用，不必重新购买。

购买前先看 [服务器准备](docs/buy-vps.md)，确认系统、公网 IP、UDP 和管理权限符合教程要求。

## 按四步完成

| 步骤 | 要完成的事 | 教程 |
| --- | --- | --- |
| 1. 准备服务器 | 选择机房与系统，准备 SSH 登录 | [购买与准备](docs/buy-vps.md) |
| 2. 部署节点 | 启动 S-UI，配置证书与三种入口 | [部署教程](docs/deployment.md) · [证书说明](docs/tls.md) |
| 3. 设置客户端 | 导入节点，检查 TUN、DNS、IPv6、WebRTC 和断线策略 | [客户端接入](docs/clients.md) · [IP 防泄露](docs/leak-protection.md) |
| 4. 验收与维护 | 逐条测试，备份配置，确认续期和重启后的行为 | [验收清单](docs/verification.md) · [维护手册](docs/maintenance.md) |

目标是让**应该经过代理的流量**使用 VPS 出口。主动设置为直连的网站仍会看到本地公网 IP。自建代理不能让你对运营商、VPS 服务商或登录账号的网站完全匿名，也不能只凭一个检测页面证明永远不会泄露。

## 现在做到哪一步

- 已有：固定镜像部署配置、三协议模板、中文流程与自动配置检查。
- 已验证：模板核心解析、Compose 配置、S-UI 隔离启动健康检查。
- 待实测：新 VPS 完整部署、真实客户端、防泄露与断线保护、证书续期。

**当前没有经过真实设备验收的全设备防泄露配置。** 下一步将用一台新 VPS，从头照教程部署；卡住的步骤直接修正文档，再重复测试。执行方式见 [实机验证流程](docs/pilot.md)。

## 让 AI 帮你部署

```text
请按 https://github.com/makerkitt/vps-privacy-guide 的教程部署我的 VPS。
先阅读 AGENTS.md 和 docs/pilot.md，按文档顺序操作。
SSH 别名：填写别名。
客户端系统和应用：填写实际使用的系统和客户端。
使用 S-UI 管理 AnyTLS、Hysteria2 和 Reality。
先检查现有服务、端口和防火墙，再部署。
账号、订阅、私钥和测试中的真实 IP 只写入私有文件。
完成节点连接后，逐项检查 DNS、IPv6、WebRTC 和断线直连。
每次补充操作都回写教程；没有实测的步骤标为待验证。
```

## 配置和进阶

- [Docker Compose](deploy/compose.yaml)：S-UI 管理入口默认仅绑定回环地址。
- [服务端模板](examples/server.json) / [客户端模板](examples/client.json)：原生 sing-box 格式，需替换占位符。客户端模板仅供本地代理测试，未配置 TUN 和断线保护。
- [不使用面板](docs/standalone.md)：直接运行 sing-box。
- [版本清单](versions.json)：固定版本与镜像摘要。

开发验证：`python3 -m unittest discover -s tests -v`；真实核心配置校验：`VALIDATE_CORE=1 python3 -m unittest discover -s tests -v`（需要 Docker 和 OpenSSL）。

本仓库原创内容使用 [MIT 许可证](LICENSE)。S-UI、sing-box 保留各自许可，见 [NOTICE.md](NOTICE.md)。
